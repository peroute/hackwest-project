import { useState } from 'react'
import Login from '/Users/aminagahramanova/Desktop/hackwest-project/front end/src/components/Login.jsx'
import ChatPage from './pages/ChatPage'
import '/Users/aminagahramanova/Desktop/hackwest-project/front end/src/styles/Login.css'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)

  const handleLogin = (username) => {
    setCurrentUser(username)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setCurrentUser(null)
    setIsLoggedIn(false)
  }

  return (
    <div className="App">
      {isLoggedIn ? (
        <ChatPage />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  )
}

export default App