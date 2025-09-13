import React from 'react';
import styles from '../styles/MessageBubble.module.css';

// MessageBubble: Renders a single chat message with role-based styling and animation
// Props: { role: 'user' | 'ai', text: string | ReactNode, timestamp?: string }
const MessageBubble = ({ role, text, timestamp }) => (
  <div
    className={
      role === 'user'
        ? `${styles.bubble} ${styles.user}`
        : `${styles.bubble} ${styles.ai}`
    }
    tabIndex={0}
    aria-label={`${role === 'user' ? 'You' : 'AI'}: ${typeof text === 'string' ? text : ''}`}
  >
    <div className={styles.text}>{text}</div>
    <div className={styles.timestamp}>{timestamp}</div>
  </div>
);

export default MessageBubble;
