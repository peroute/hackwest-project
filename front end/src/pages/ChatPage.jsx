import React from 'react';
import ChatScreen from '/Users/aminagahramanova/Desktop/hackwest-project/front end/src/pages/ChatScreen.jsx';
import styles from '/Users/aminagahramanova/Desktop/hackwest-project/front end/src/App.module.css';

const Logo = () => (
  <div className={styles.logo} aria-label="Texas Tech University Logo" />
);

const ChatPage = () => (
  <div className={styles.appContainer}>
    <header className={styles.header}>
      <Logo />
      <h1 className={styles.title}>Texas Tech University AI Chat</h1>
    </header>
    <main className={styles.main}>
      <ChatScreen />
    </main>
    <footer className={styles.footer}>
      &copy; {new Date().getFullYear()} Texas Tech University. All rights reserved.
    </footer>
  </div>
);

export default ChatPage;