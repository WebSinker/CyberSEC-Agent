# CTF Assistant - Quick Setup Guide

## Project Overview
CTF Assistant is an AI-powered tool that helps analyze Capture The Flag (CTF) cybersecurity challenges, providing insights, tool recommendations, and step-by-step guidance.

## Project Structure
```
CYBERSEC-AGENT/
│
├── backend/                    # FastAPI backend server
│   ├── __pycache__/            # Python bytecode cache
│   ├── temp/                   # Temporary storage for uploaded files
│   └── Main.py                 # FastAPI backend implementation
│
├── src/                        # React frontend source files
│   ├── App.css                 # Styling for the main React component
│   ├── App.jsx                 # Main React component
│   └── index.jsx               # React entry point
│
├── node_modules/               # Node.js dependencies
├── .env                        # Environment variables
├── CTF.png                     # Project logo/screenshot
├── index.html                  # HTML entry point for the React app
├── package.json                # NPM configuration
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── vite.config.js              # Vite configuration for the frontend
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- Tesseract OCR
- Google Gemini API key

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/cybersec-agent.git
cd cybersec-agent
```

### Step 2: Set Up Backend

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Tesseract OCR:
   - Make sure Tesseract is installed on your system
   - Update the path in `backend/Main.py` if necessary:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. Create `.env` file in the project root with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

### Step 3: Set Up Frontend

1. Install Node.js dependencies:
```bash
npm install
```

2. If any issues with dependencies, run:
```bash
npm install react react-dom
npm install --save-dev @vitejs/plugin-react vite
```

### Step 4: Run the Application

1. Start the backend server:
```bash
cd backend
uvicorn Main:app --reload --host 0.0.0.0 --port 8000
```

2. In a new terminal, start the frontend development server:
```bash
npm run dev
```

3. Access the application at http://localhost:3000

## Using the CTF Assistant

1. **Upload a Challenge**:
   - Enter the challenge description
   - Upload any relevant files (binaries, images, etc.)
   - Upload screenshots if available

2. **Analyze**:
   - Click "Analyze Challenge" to get AI-powered insights
   - Review the structured analysis with challenge type, tools, approach, and clues

3. **Chat Interface**:
   - Ask follow-up questions about the challenge
   - Get guidance on using recommended tools
   - Explore alternative approaches

## Troubleshooting

### Backend Issues

1. **"libmagic not found" error**:
   ```bash
   pip uninstall python-magic
   pip install python-magic-bin
   ```

2. **Tesseract OCR not found**:
   - Ensure Tesseract is installed
   - Check the path in Main.py matches your installation

### Frontend Issues

1. **Connection errors with backend**:
   - Verify backend is running on port 8000
   - Check proxy settings in vite.config.js
   - Ensure CORS is properly configured

2. **Rendering issues**:
   - Check browser console for errors
   - Verify all React dependencies are installed

## Advanced Configuration

- **Change Gemini model**: Edit the model name in Main.py
  ```python
  model = genai.GenerativeModel('gemini-2.0-flash')  # or 'gemini-pro'
  ```

- **Modify proxy settings**: Update vite.config.js if your backend is on a different URL
  ```javascript
  server: {
    proxy: {
      '/analyze': 'http://your-backend-url:8000',
      '/chat': 'http://your-backend-url:8000'
    }
  }
  ```