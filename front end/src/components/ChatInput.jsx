import React, { useState, useRef, useEffect } from 'react';
import styles from '../styles/ChatInput.module.css';

// ChatInput: Controlled textarea with send button, keyboard accessibility, and auto-resize
// Props: { onSend: function, loading?: boolean, disabled?: boolean }
const ChatInput = ({ onSend, loading, disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  // Handle Enter (send), Shift+Enter (newline)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    setInput('');
    await onSend(trimmed);
  };

  return (
    <form
      className={styles.inputBar}
      onSubmit={(e) => {
        e.preventDefault();
        handleSend();
      }}
      aria-label="Send a message"
    >
      <textarea
        ref={textareaRef}
        className={styles.textarea}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message…"
        rows={1}
        disabled={disabled}
        aria-label="Message input"
        autoFocus
      />
      <button
        type="submit"
        className={styles.sendBtn}
        disabled={loading || !input.trim()}
        aria-label="Send message"
      >
        Send
      </button>
    </form>
  );
};

export default ChatInput;
