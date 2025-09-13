import { useState } from 'react';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Simple validation
    if (!formData.username || !formData.password) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    // Simulate login process
    try {
      // In a real app, this would be an API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes, accept any non-empty credentials
      if (formData.username.trim() && formData.password.trim()) {
        onLogin(formData.username);
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-title">TTU Login</h1>
        <p style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--ttu-gray)' }}>
          Welcome to Texas Tech University
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username or Email
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your username or email"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="form-input"
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          {error && (
            <div style={{ 
              color: 'var(--ttu-red)', 
              marginBottom: '1rem', 
              textAlign: 'center',
              fontSize: '0.9rem'
            }}>
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="ttu-button"
            disabled={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div style={{ 
          marginTop: '2rem', 
          textAlign: 'center', 
          fontSize: '0.9rem',
          color: 'var(--ttu-gray)'
        }}>
          <p>Demo: Use any username and password to login</p>
          <p style={{ marginTop: '0.5rem' }}>
            <a href="#" style={{ color: 'var(--ttu-red)' }}>Forgot Password?</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;