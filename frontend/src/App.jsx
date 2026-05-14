import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your SHL Assessment Recommender. Which role are you looking to hire for today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('https://shlrecommender-production.up.railway.app/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages })
      });

      const data = await response.json();
      setMessages([...newMessages, {
        role: 'assistant',
        content: data.reply,
        recommendations: data.recommendations
      }]);
    } catch (error) {
      console.error("Error calling API:", error);
      setMessages([...newMessages, {
        role: 'assistant',
        content: "I'm sorry, I encountered an error connecting to the server. Please make sure the backend is running on port 8000."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <div className="logo-container">
          <div className="logo-icon">SHL</div>
          <div className="logo-text">
            <h1>Assessment Recommender</h1>
            <p>Powered by Talent Intelligence</p>
          </div>
        </div>
        <div className="status-badge" style={{ color: 'var(--success)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '8px', height: '8px', background: 'var(--success)', borderRadius: '50%' }}></span>
          System Active
        </div>
      </header>

      <main className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
            {msg.recommendations && msg.recommendations.length > 0 && (
              <div className="recommendations">
                {msg.recommendations.map((rec, rIdx) => (
                  <div key={rIdx} className="rec-card">
                    <h4>{rec.name}</h4>
                    <p>Type: {rec.test_type === 'K' ? 'Cognitive' : rec.test_type === 'P' ? 'Personality' : 'Skills'}</p>
                    <a href={rec.url} target="_blank" rel="noopener noreferrer" className="rec-link">View Details →</a>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="typing-indicator">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>

      <div className="input-area">
        <input
          type="text"
          placeholder="Ask about assessments for a Java Developer, Sales Manager..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;
