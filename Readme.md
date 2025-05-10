# CTF Assistant

An AI-powered assistant designed to help CTF (Capture The Flag) participants analyze challenges and develop solution strategies.

![CTF Assistant Screenshot](screenshot.png)

## Features

- **Challenge Analysis**: Upload challenge files, screenshots, and descriptions to get AI-powered insights
- **Multi-format Support**: Handles various file types including executables, text files, and images
- **Interactive Chat**: Engage in a conversation with the AI to refine your approach and get additional guidance
- **Steganography Detection**: Basic identification of hidden data in images
- **Binary Analysis**: Extracts interesting strings from executable files
- **OCR Capabilities**: Extract text from challenge screenshots
- **Structured Output**: Cleanly formatted analysis with challenge type, recommended tools, approach steps, and potential clues

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#usage)
  - [Starting the Application](#starting-the-application)
  - [Analyzing a Challenge](#analyzing-a-challenge)
  - [Using the Chat Interface](#using-the-chat-interface)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 14+ (for frontend)
- Tesseract OCR (for screenshot text extraction)
- Google Gemini API key

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ctf-assistant.git
   cd ctf-assistant
   ```

2. Set up a virtual environment(optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies(or use the requirements.txt):
   ```bash
   pip install fastapi uvicorn python-multipart python-magic-bin pytesseract pillow google-generativeai python-dotenv
   ```

4. Install Tesseract OCR:
   - **Windows**: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt install tesseract-ocr`

5. Create a `.env` file in the backend directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

### Starting the Application

1. Start the backend server (from the project root):
   ```bash
   cd backend
   uvicorn Main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start the frontend development server (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

### Analyzing a Challenge

1. Enter the challenge description or hints in the text area
2. Upload the challenge file if available (binary, text file, image, etc.)
3. Upload a screenshot of the challenge if available
4. Click "Analyze Challenge"
5. Review the AI-generated analysis in the chat section

### Using the Chat Interface

After analyzing a challenge, you can:

1. Ask follow-up questions about specific aspects of the challenge
2. Request additional tool recommendations
3. Get help with specific techniques mentioned in the analysis
4. Explore alternative approaches

Example questions:
- "How do I use steghide to check for hidden data?"
- "Can you explain more about the LSB technique mentioned?"
- "What would be the next step if I find encoded data in the image?"
- "How can I detect if there's a substitution cipher being used?"

## Configuration

### Backend Configuration

- **Tesseract Path**: If Tesseract OCR is installed in a non-standard location, update the path in `Main.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'C:\Path\To\Tesseract\tesseract.exe'
  ```

- **API Model**: You can change the Gemini model by modifying the model parameter in `Main.py`:
  ```python
  model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-pro'
  ```

### Frontend Configuration

- **Backend URL**: If you need to change the backend URL, update the proxy settings in `vite.config.js`:
  ```javascript
  server: {
    port: 3000,
    proxy: {
      '/analyze': 'http://your-backend-url:8000',
      '/chat': 'http://your-backend-url:8000'
    }
  }
  ```

## Contributing

Contributions are welcome! Here are some ways you can contribute to the project:

- Adding support for more CTF challenge types
- Improving the frontend UI
- Adding more sophisticated analysis techniques
- Fixing bugs and improving error handling
- Enhancing documentation

Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
- [Google Gemini API](https://ai.google.dev/gemini-api)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)