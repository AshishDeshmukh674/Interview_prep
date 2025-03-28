import React, { useEffect } from 'react';

const App = () => {
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/start-session');
        const data = await response.json();
        if (data.session_id) {
          localStorage.setItem('sessionId', data.session_id);
          console.log('Session initialized:', data.session_id);
        }
      } catch (error) {
        console.error('Failed to initialize session:', error);
      }
    };

    initSession(); // Always initialize session when app loads
  }, []);

  return (
    <div className="App">
      {/* Your existing components */}
    </div>
  );
};

export default App; 