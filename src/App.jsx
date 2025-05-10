import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [screenshot, setScreenshot] = useState(null);
  const [challenge, setChallenge] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [chat, setChat] = useState([]);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleScreenshotChange = (e) => {
    setScreenshot(e.target.files[0]);
  };

  const handleChallengeChange = (e) => {
    setChallenge(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData();
    if (file) formData.append('file', file);
    if (screenshot) formData.append('screenshot', screenshot);
    formData.append('challenge', challenge);

    try {
      // Using relative URL to work with the proxy
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
      
      // Add the system message to chat
      setChat(prevChat => [
        ...prevChat, 
        { 
          role: 'system', 
          content: data.initial_analysis || "Analysis complete. You can now ask follow-up questions."
        }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'An error occurred during analysis' });
      
      // Add error message to chat
      setChat(prevChat => [
        ...prevChat,
        {
          role: 'system',
          content: 'There was an error connecting to the analysis server. Please check if the backend is running on port 8000.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMessageSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to chat
    setChat(prevChat => [
      ...prevChat,
      { role: 'user', content: message }
    ]);

    const currentMessage = message;
    setMessage(''); // Clear input field immediately
    setIsLoading(true);

    try {
      // Using relative URL to work with the proxy
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          history: chat,
          result: result,
        }),
      });

      const data = await response.json();
      
      // Add the system response to chat
      setChat(prevChat => [
        ...prevChat,
        { role: 'system', content: data.response }
      ]);
    } catch (error) {
      console.error('Error:', error);
      setChat(prevChat => [
        ...prevChat,
        { role: 'system', content: 'An error occurred. Please check if the backend server is running.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to render message content
  const renderMessageContent = (content, role) => {
    // Only use dangerouslySetInnerHTML for system messages, not user messages
    if (role === 'user') {
      return content; // Return plain text for user messages
    } else {
      return <div dangerouslySetInnerHTML={{ __html: content }} />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CTF Assistant</h1>
      </header>
      <main>
        <div className="upload-section">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="challenge">Challenge Description or Hint:</label>
              <textarea
                id="challenge"
                value={challenge}
                onChange={handleChallengeChange}
                placeholder="Enter the challenge description, hint, or any information provided"
                rows={4}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="file">Upload Challenge File (if available):</label>
              <input
                type="file"
                id="file"
                onChange={handleFileChange}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="screenshot">Upload Screenshot (if available):</label>
              <input
                type="file"
                id="screenshot"
                accept="image/*"
                onChange={handleScreenshotChange}
              />
            </div>
            
            <button type="submit" disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Analyze Challenge'}
            </button>
          </form>
        </div>
        
        <div className="chat-section">
          <div className="chat-messages">
            {chat.length === 0 ? (
              <div className="message system-message">
                Welcome to CTF Assistant! Upload a challenge and I'll help you analyze it.
              </div>
            ) : (
              chat.map((msg, index) => (
                <div 
                  key={index} 
                  className={`message ${msg.role === 'user' ? 'user-message' : 'system-message'}`}
                >
                  {renderMessageContent(msg.content, msg.role)}
                </div>
              ))
            )}
            {isLoading && (
              <div className="message system-message loading">
                Working on it...
              </div>
            )}
          </div>
          
          <form onSubmit={handleMessageSubmit} className="chat-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask a follow-up question..."
              disabled={isLoading || chat.length === 0}
            />
            <button type="submit" disabled={isLoading || !message.trim() || chat.length === 0}>
              Send
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;