from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
import subprocess
import uuid
import pytesseract
from PIL import Image
import io
import json
import magic
import google.generativeai as genai  # For the Gemini LLM integration
import os
from dotenv import load_dotenv
import re

# Set up Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load environment variables
load_dotenv()
import base64
import hashlib

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create temp directory if it doesn't exist
os.makedirs("./temp", exist_ok=True)

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]]
    result: Optional[Dict[str, Any]] = None
    
# Add this formatter function to your Main.py file

def format_llm_response(raw_response):
    """
    Format the raw LLM response into a structured format for better readability.
    """
    # Handle asterisks and bold text in the raw response
    # Replace markdown-style **text** with HTML <strong>text</strong>
    formatted_text = raw_response.replace("**", "<strong>", 1)
    while "**" in formatted_text:
        formatted_text = formatted_text.replace("**", "</strong>", 1)
        if "**" in formatted_text:
            formatted_text = formatted_text.replace("**", "<strong>", 1)
    
    # First try to identify if the response has clear sections
    sections = {
        "challenge_type": [],
        "tools": [],
        "steps": [],
        "clues": []
    }
    
    current_section = None
    lines = formatted_text.split('\n')
    
    # Try to identify numbered sections like "1. Challenge Type:" in the response
    section_mapping = {
        "1": "challenge_type",
        "2": "tools",
        "3": "steps",
        "4": "clues"
    }
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # First try to identify numbered sections
        if line.startswith(("1.", "2.", "3.", "4.")) and ":" in line:
            section_num = line[0]
            if section_num in section_mapping:
                current_section = section_mapping[section_num]
                # Store the section header
                sections[current_section].append(line)
                continue
                
        # If not numbered, try keyword identification    
        lower_line = line.lower()
        if "challenge type" in lower_line or "likely to be" in lower_line or "ctf category" in lower_line:
            current_section = "challenge_type"
            sections[current_section].append(line)
            continue
        elif "tool" in lower_line or "technique" in lower_line:
            current_section = "tools"
            sections[current_section].append(line)
            continue
        elif "step" in lower_line or "next" in lower_line or "approach" in lower_line:
            current_section = "steps"
            sections[current_section].append(line)
            continue
        elif "clue" in lower_line or "hidden" in lower_line or "pattern" in lower_line:
            current_section = "clues"
            sections[current_section].append(line)
            continue
            
        # Add content to the current section
        if current_section:
            sections[current_section].append(line)
    
    # Format into a clean, structured response
    formatted = []
    
    # Challenge Type Section
    formatted.append("<div class='analysis-section'>")
    formatted.append("<h3>Challenge Type</h3>")
    if sections["challenge_type"]:
        # Process the content to properly identify paragraphs
        paragraphs = []
        current_para = []
        
        for line in sections["challenge_type"]:
            # Skip section headers that were already processed
            if line.startswith(("1.", "2.", "3.", "4.")) and ":" in line:
                continue
                
            # If line is a bullet point, it's a new item
            if line.lstrip().startswith(("*", "-", "•")):
                # If we were building a paragraph, add it
                if current_para:
                    paragraphs.append(" ".join(current_para))
                    current_para = []
                # Add this as a bullet point
                paragraphs.append(line)
            else:
                # Add to current paragraph
                current_para.append(line)
        
        # Add final paragraph if exists
        if current_para:
            paragraphs.append(" ".join(current_para))
        
        # Output paragraphs
        for para in paragraphs:
            if para.lstrip().startswith(("*", "-", "•")):
                # Create bullet list if needed
                if not formatted_text.endswith("</ul>"):
                    formatted.append("<ul>")
                formatted.append(f"<li>{para.lstrip('*- •')}</li>")
            else:
                # Close bullet list if we were in one
                if formatted_text.endswith("</li>"):
                    formatted.append("</ul>")
                formatted.append(f"<p>{para}</p>")
    else:
        # Fallback if sections aren't clearly identified
        formatted.append("<p>Based on the available information, this appears to be a challenge that requires careful analysis.</p>")
    formatted.append("</div>")
    
    # Tools Section
    formatted.append("<div class='analysis-section'>")
    formatted.append("<h3>Recommended Tools</h3>")
    if sections["tools"]:
        formatted.append("<ul>")
        in_nested_list = False
        
        for tool in sections["tools"]:
            # Skip section headers
            if tool.startswith(("1.", "2.", "3.", "4.")) and ":" in tool:
                continue
                
            # Clean up bullet points and asterisks
            clean_tool = tool.lstrip("*-• ")
            
            # Check if this is a nested list item (indented bullet)
            if tool.startswith(("  *", "  -", "  •", "\t*", "\t-", "\t•")):
                if not in_nested_list:
                    # Start a nested list
                    formatted.append("<ul>")
                    in_nested_list = True
                formatted.append(f"<li>{clean_tool}</li>")
            else:
                # If we were in a nested list, close it
                if in_nested_list:
                    formatted.append("</ul>")
                    in_nested_list = False
                
                # Normal list item
                if tool.lstrip().startswith(("*", "-", "•")):
                    formatted.append(f"<li>{clean_tool}</li>")
                else:
                    # This is a paragraph, not a list item
                    if tool and len(tool) > 5:
                        formatted.append(f"<li>{tool}</li>")
        
        # Close any open nested list
        if in_nested_list:
            formatted.append("</ul>")
            
        formatted.append("</ul>")
    else:
        formatted.append("<p>Several specialized tools could be useful for this challenge.</p>")
    formatted.append("</div>")
    
    # Steps Section
    formatted.append("<div class='analysis-section'>")
    formatted.append("<h3>Recommended Approach</h3>")
    if sections["steps"]:
        formatted.append("<ol>")
        
        for step in sections["steps"]:
            # Skip section headers
            if step.startswith(("1.", "2.", "3.", "4.")) and ":" in step:
                continue
                
            # Check if it's already a numbered step
            if re.match(r'^\d+\.', step.lstrip()):
                # Clean up numbering
                clean_step = re.sub(r'^\d+\.', '', step.lstrip()).strip()
                formatted.append(f"<li>{clean_step}</li>")
            # Or a bullet point
            elif step.lstrip().startswith(("*", "-", "•")):
                # Clean up bullet
                clean_step = step.lstrip("*-• ").strip()
                formatted.append(f"<li>{clean_step}</li>")
            # Or just plain text (make it a step if it's substantial)
            elif step and len(step) > 5:
                formatted.append(f"<li>{step}</li>")
                
        formatted.append("</ol>")
    else:
        formatted.append("<p>A systematic approach is recommended for this challenge.</p>")
    formatted.append("</div>")
    
    # Clues Section
    formatted.append("<div class='analysis-section'>")
    formatted.append("<h3>Potential Clues</h3>")
    if sections["clues"]:
        formatted.append("<ul>")
        for clue in sections["clues"]:
            # Skip section headers
            if clue.startswith(("1.", "2.", "3.", "4.")) and ":" in clue:
                continue
                
            # Check if it's a bullet point
            if clue.lstrip().startswith(("*", "-", "•")):
                clean_clue = clue.lstrip("*-• ").strip()
                formatted.append(f"<li>{clean_clue}</li>")
            # Or just plain text (make it a clue if it's substantial)
            elif clue and len(clue) > 5:
                formatted.append(f"<li>{clue}</li>")
                
        formatted.append("</ul>")
    else:
        formatted.append("<p>Look for unusual patterns or hidden information in the provided materials.</p>")
    formatted.append("</div>")
    
    # Format code blocks
    result = "\n".join(formatted)
    result = result.replace("`", "<code>", 1)
    while "`" in result:
        result = result.replace("`", "</code>", 1)
        if "`" in result:
            result = result.replace("`", "<code>", 1)
    
    return result

@app.post("/analyze")
async def analyze_challenge(
    file: Optional[UploadFile] = File(None),
    screenshot: Optional[UploadFile] = File(None),
    challenge: str = Form("")
):
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    session_dir = f"./temp/{session_id}"
    os.makedirs(session_dir, exist_ok=True)
    
    analysis_results = {
        "session_id": session_id,
        "challenge_text": challenge,
        "file_analysis": None,
        "screenshot_analysis": None,
        "possible_categories": [],
        "suggested_tools": [],
        "initial_thoughts": ""
    }
    
    # Process uploaded file if available
    if file:
        file_path = f"{session_dir}/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Basic file analysis
        analysis_results["file_analysis"] = await analyze_file(file_path)
    
    # Process screenshot if available
    if screenshot:
        screenshot_path = f"{session_dir}/screenshot.png"
        with open(screenshot_path, "wb") as buffer:
            shutil.copyfileobj(screenshot.file, buffer)
        
        # Extract text from screenshot
        analysis_results["screenshot_analysis"] = extract_text_from_image(screenshot_path)
    
    # Combine all information and use LLM for initial analysis
    if challenge or analysis_results["file_analysis"] or analysis_results["screenshot_analysis"]:
        analysis_results["initial_analysis"] = await get_llm_analysis(analysis_results)
    
    return JSONResponse(content=analysis_results)

@app.post("/chat")
async def chat(request: ChatRequest):
    # Process the chat message using the LLM
    response = await process_chat_message(
        request.message, 
        request.history, 
        request.result
    )
    
    return JSONResponse(content={"response": response})

async def analyze_file(file_path: str) -> Dict[str, Any]:
    """Perform basic analysis on the uploaded file."""
    result = {}
    
    # Get file type
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    result["file_type"] = file_type
    
    # Get file size
    file_size = os.path.getsize(file_path)
    result["file_size"] = file_size
    
    # Calculate file hash
    with open(file_path, "rb") as f:
        file_data = f.read()
        result["md5"] = hashlib.md5(file_data).hexdigest()
        result["sha1"] = hashlib.sha1(file_data).hexdigest()
    
    # Run basic analysis based on file type
    if "text/" in file_type:
        with open(file_path, "r", errors="ignore") as f:
            content = f.read(4096)  # Read first 4KB
            result["preview"] = content
    
    elif "image/" in file_type:
        # Check for steganography (basic)
        try:
            # Just an example - you'd want more sophisticated steg analysis
            output = subprocess.check_output(["strings", file_path], text=True)
            interesting_strings = [s for s in output.split('\n') if len(s) > 8]
            if interesting_strings:
                result["interesting_strings"] = interesting_strings[:10]  # First 10 strings
        except Exception as e:
            result["steg_analysis_error"] = str(e)
    
    elif "application/x-executable" in file_type or "application/x-elf" in file_type:
        # Basic binary analysis
        try:
            output = subprocess.check_output(["strings", file_path], text=True)
            interesting_strings = [s for s in output.split('\n') if len(s) > 8]
            if interesting_strings:
                result["interesting_strings"] = interesting_strings[:20]
        except Exception as e:
            result["binary_analysis_error"] = str(e)
    
    # Add more specialized analysis based on file types
    # This is just a starting point
    
    return result

def extract_text_from_image(image_path: str) -> Dict[str, Any]:
    """Extract text from an uploaded screenshot."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        
        return {
            "extracted_text": text,
            "image_size": f"{image.width}x{image.height}"
        }
    except Exception as e:
        return {"error": str(e)}

async def get_llm_analysis(data: Dict[str, Any]) -> str:
    """Use Gemini to analyze the challenge based on available data."""
    
    # Construct the prompt for the LLM
    prompt = "As a CTF challenge analyzer, provide insights based on the following information:\n\n"
    
    if data["challenge_text"]:
        prompt += f"Challenge description: {data['challenge_text']}\n\n"
    
    if data["screenshot_analysis"] and "extracted_text" in data["screenshot_analysis"]:
        prompt += f"Text extracted from screenshot: {data['screenshot_analysis']['extracted_text']}\n\n"
    
    if data["file_analysis"]:
        prompt += "File analysis:\n"
        prompt += f"- Type: {data['file_analysis'].get('file_type', 'unknown')}\n"
        prompt += f"- Size: {data['file_analysis'].get('file_size', 'unknown')} bytes\n"
        
        if "interesting_strings" in data["file_analysis"]:
            prompt += "- Notable strings found in the file:\n"
            for s in data["file_analysis"]["interesting_strings"][:5]:  # Limit to 5 for brevity
                prompt += f"  * {s}\n"
        
        if "preview" in data["file_analysis"]:
            prompt += f"- Content preview: {data['file_analysis']['preview'][:500]}...\n"
    
    prompt += "\nBased on this information:\n"
    prompt += "1. What type of CTF challenge is this likely to be?\n"
    prompt += "2. What techniques or tools would be most useful to investigate this challenge?\n"
    prompt += "3. What are the next steps you would recommend to solve this challenge?\n"
    prompt += "4. Are there any hidden clues or patterns you can identify?\n"
    
    try:
        # Use Gemini Pro or the most capable model available
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        system_prompt = "You are a specialized cybersecurity assistant that helps with CTF challenges. You have expertise in various security domains including cryptography, web exploitation, forensics, reverse engineering, binary exploitation, and steganography."
        
        # Gemini uses a different API structure compared to OpenAI
        response = model.generate_content(
            [
                {"role": "user", "parts": [system_prompt + "\n\n" + prompt]}
            ]
        )
        
        # FIXED: Apply formatting to the response and return the formatted version
        formatted_response = format_llm_response(response.text)
        return formatted_response  # Return the formatted response, not the raw text
    except Exception as e:
        return f"Error analyzing challenge: {str(e)}"

async def process_chat_message(message: str, history: List[Dict[str, str]], result: Optional[Dict[str, Any]]) -> str:
    """Process a chat message using Gemini."""
    
    system_prompt = """You are a specialized cybersecurity assistant for CTF challenges. 
    You have expertise in various security domains including cryptography, web exploitation, 
    forensics, reverse engineering, binary exploitation, and steganography. 
    Your goal is to guide the user through solving CTF challenges by providing 
    hints, tool suggestions, and methodology, but without directly solving the challenge for them."""
    
    # Convert our history format to Gemini's format
    gemini_messages = []
    
    # Add system prompt to the first message
    first_message = True
    
    # Add conversation history
    for msg in history:
        role = "model" if msg["role"] == "system" else "user"
        
        if first_message and role == "user":
            content = system_prompt + "\n\n" + msg["content"]
            first_message = False
        else:
            content = msg["content"]
            
        gemini_messages.append({"role": role, "parts": [content]})
    
    # If we haven't added the system prompt yet, add it to the current message
    if first_message:
        current_message = system_prompt + "\n\n" + message
        first_message = False
    else:
        current_message = message
    
    # Add the current message
    gemini_messages.append({"role": "user", "parts": [current_message]})
    
    # If we have analysis results, provide them to the LLM as additional context
    if result:
        context = "Here's what I know about the challenge so far:\n"
        if "challenge_text" in result and result["challenge_text"]:
            context += f"Challenge description: {result['challenge_text']}\n"
        
        if "initial_analysis" in result and result["initial_analysis"]:
            context += f"Initial analysis: {result['initial_analysis']}\n"
        
        # Add this context to the last message
        gemini_messages[-1]["parts"][0] += "\n\n" + context
    
    try:
        # Use Gemini Pro or the most capable model available
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate a response using the conversation history
        chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
        response = chat.send_message(gemini_messages[-1]["parts"][0])
        
        #Add formatting
        formatted_response = format_llm_response(response.text)
        return formatted_response  # Return the formatted response, not the raw text
    except Exception as e:
        return f"Error processing your message: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)