# Texas Tech University AI Chat

A modern, accessible AI chat web app for Texas Tech University resources, built with React 18 and Vite.

## Features

- Responsive, accessible chat UI with Texas Tech branding
- Modular CSS (CSS Modules) and global CSS reset
- Message list with auto-scroll, timestamps, and loading indicator
- Inline error handling and retry
- Keyboard accessible input (Enter to send, Shift+Enter for newline)
- Placeholder backend endpoint

## Getting Started

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the app locally:**
   ```bash
   npm run dev
   ```

3. **Open in your browser:**
   - Visit [http://localhost:5173](http://localhost:5173) (default Vite port)

## Backend Endpoint

- The frontend sends chat requests to a placeholder backend at:
  ```
  http://localhost:5000/chat
  ```
- To change this, edit the `CHAT_ENDPOINT` constant in `src/pages/ChatScreen.jsx`.

## Project Structure

- `src/components/` – Reusable UI components
- `src/pages/` – Main chat screen
- `src/styles/` – CSS modules and global styles

## Customization

- Replace the logo placeholder in `src/App.jsx` and `App.module.css` with the official Texas Tech logo if desired.
- Adjust colors in `src/styles/global.css` for further branding.

---

**This project is frontend-only.** You must provide a backend at the specified endpoint for full functionality.
