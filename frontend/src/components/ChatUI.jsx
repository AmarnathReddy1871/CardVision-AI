import React, { useState, useRef, useEffect } from 'react';
import './ChatUI.css';

const ChatUI = () => {
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [userId] = useState(() => `user_${Math.random().toString(36).substr(2, 9)}`);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [sessionState, setSessionState] = useState(null);
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send message to API
  const sendMessage = async (imageBase64 = null, audioBase64 = null) => {
    if (!inputValue.trim() && !imageBase64 && !audioBase64) return;

    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: userId,
          message: inputValue,
          image_base64: imageBase64,
          audio_base64: audioBase64,
        }),
      });

      const data = await response.json();

      // Add user message
      if (inputValue.trim()) {
        setMessages(prev => [...prev, {
          type: 'user',
          content: inputValue,
          timestamp: new Date(),
        }]);
      }

      // Add bot responses
      if (data.messages) {
        data.messages.forEach(msg => {
          setMessages(prev => [...prev, {
            type: 'bot',
            ...msg,
            timestamp: new Date(),
          }]);
        });
      }

      // Update session state
      if (data.session_state) {
        setSessionState(data.session_state);
      }

      setInputValue('');
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Failed to send message. Please try again.',
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      const base64 = event.target?.result.split(',')[1];
      
      setMessages(prev => [...prev, {
        type: 'user',
        content: '📸 Uploaded card image',
        timestamp: new Date(),
      }]);

      await sendMessage(base64);
    };
    reader.readAsDataURL(file);
  };

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const reader = new FileReader();
        reader.onload = async (event) => {
          const base64 = event.target?.result.split(',')[1];
          setMessages(prev => [...prev, {
            type: 'user',
            content: '🎤 Voice note recorded',
            timestamp: new Date(),
          }]);
          await sendMessage(null, base64);
        };
        reader.readAsDataURL(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Recording error:', error);
      alert('Microphone permission required');
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>📇 Card Digitization Assistant</h1>
        <p className="session-info">Session: {sessionId.slice(0, 12)}...</p>
        {sessionState && (
          <div className="state-indicator">
            Status: <span className="state-badge">{sessionState.step}</span>
          </div>
        )}
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>Upload a visiting card image to get started:</p>
            <ul>
              <li>📸 Upload a card image</li>
              <li>✨ AI extracts the details</li>
              <li>💾 Data saved to Google Sheets</li>
              <li>📱 Manager notified via WhatsApp</li>
              <li>🎤 Add voice notes</li>
            </ul>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message message-${msg.type}`}>
              {msg.type === 'user' && (
                <div className="user-message">
                  <span className="message-content">{msg.content}</span>
                </div>
              )}

              {msg.type === 'bot' && (
                <div className="bot-message">
                  <span className={`message-badge badge-${msg.type}`}>
                    {msg.type === 'confirmation' && '✓'}
                    {msg.type === 'success' && '✅'}
                    {msg.type === 'error' && '❌'}
                    {msg.type === 'warning' && '⚠️'}
                    {msg.type === 'info' && 'ℹ️'}
                    {msg.type === 'status' && '⏳'}
                    {msg.type === 'prompt' && '❓'}
                  </span>
                  <span className="message-content">{msg.content}</span>
                </div>
              )}

              {msg.type === 'error' && (
                <div className="error-message">
                  <span>❌ {msg.content}</span>
                </div>
              )}

              {msg.contact && (
                <div className="contact-card">
                  <h3>{msg.contact.name}</h3>
                  <p>📞 {msg.contact.phone || 'N/A'}</p>
                  <p>📧 {msg.contact.email || 'N/A'}</p>
                  <p>🏢 {msg.contact.company || 'N/A'}</p>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="input-controls">
          <button
            className="btn btn-icon"
            onClick={() => fileInputRef.current?.click()}
            title="Upload card image"
            disabled={isLoading}
          >
            📸 Upload Card
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }}
          />

          <button
            className={`btn btn-icon ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            title={isRecording ? 'Stop recording' : 'Start recording'}
            disabled={isLoading}
          >
            🎤 {isRecording ? 'Stop' : 'Record'}
          </button>
        </div>

        <div className="input-group">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
            placeholder="Type a message or upload a card image..."
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || (!inputValue.trim())}
            className="btn-send"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatUI;
