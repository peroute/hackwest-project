import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from '../components/MessageBubble';
import ChatInput from '../components/ChatInput';
import LoadingSpinner from '../components/LoadingSpinner';
import styles from '../styles/ChatScreen.module.css';

// Helper to format time as HH:MM
const formatTime = (date) => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const CHAT_ENDPOINT = 'http://localhost:5468/api/Gemini/generate';

const ChatScreen = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [pendingUserMsg, setPendingUserMsg] = useState(null); // For retry

  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Send message to backend
  const sendMessage = async (userText) => {
    setError('');
    setLoading(true);
    setPendingUserMsg(null);

    const userMsg = {
      role: 'user',
      text: userText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch(CHAT_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userText }),
      });

      if (!res.ok) throw new Error('Network error');
      const data = await res.json();

      if (!data) throw new Error('Invalid response from server');

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          text: data.text,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError('Failed to get response. Please try again.');
      setPendingUserMsg(userMsg);
    } finally {
      setLoading(false);
    }
  };

  // Retry last user message
  const handleRetry = async () => {
    if (pendingUserMsg) {
      setError('');
      setLoading(true);
      try {
        const res = await fetch(CHAT_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: pendingUserMsg.text }),
        });

        if (!res.ok) throw new Error('Network error');
        const data = await res.json();

        if (!data) throw new Error('Invalid response from server');

        setMessages((prev) => [
          ...prev,
          {
            role: 'ai',
            text: data.text,
            timestamp: new Date().toISOString(),
          },
        ]);
        setPendingUserMsg(null);
      } catch (err) {
        setError('Failed to get response. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <section className={styles.chatScreen} aria-label="AI Chat Conversation">
      <div className={styles.messagesContainer} role="log" aria-live="polite">
        {messages.map((msg, idx) => (
          <MessageBubble
            key={idx}
            role={msg.role}
            text={msg.text}
            timestamp={formatTime(msg.timestamp)}
          />
        ))}
        {loading && (
          <div className={styles.loadingBubble}>
            <MessageBubble
              role="ai"
              text={
                <span className={styles.typing}>
                  <LoadingSpinner size={18} /> AI is typing...
                </span>
              }
              timestamp={formatTime(new Date())}
            />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {error && (
        <div className={styles.errorBar} role="alert">
          <span>{error}</span>
          {pendingUserMsg && (
            <button
              className={styles.retryBtn}
              onClick={handleRetry}
              disabled={loading}
              aria-label="Retry sending message"
            >
              Retry
            </button>
          )}
        </div>
      )}
      <ChatInput
        onSend={sendMessage}
        loading={loading}
        disabled={loading}
      />
    </section>
  );
};

export default ChatScreen;
