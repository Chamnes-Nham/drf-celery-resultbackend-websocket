// import React, { useState } from 'react';
// import axios from 'axios';

// const Login = () => {
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');
//   const [message, setMessage] = useState('');

//   const handleLogin = async (e) => {
//     e.preventDefault();

//     try {
//       const response = await axios.post('http://localhost:8000/api/login/', { username, password });
//       if (response.status === 200) {
//         setMessage('Login successful!');
//         // Redirect or update UI as needed
//       }
//     } catch (error) {
//       setMessage('Login failed. Please check your credentials and try again.');
//     }
//   };

//   return (
//     <div>
//       <h2>Login</h2>
//       <form onSubmit={handleLogin}>
//         <input
//           type="text"
//           placeholder="Username"
//           value={username}
//           onChange={(e) => setUsername(e.target.value)}
//           required
//         />
//         <input
//           type="password"
//           placeholder="Password"
//           value={password}
//           onChange={(e) => setPassword(e.target.value)}
//           required
//         />
//         <button type="submit">Login</button>
//       </form>
//       <p>{message}</p>
//     </div>
//   );
// };

// export default Login;


import axios from 'axios';
import React, { useState, useEffect } from 'react';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Fetch and store the CSRF token from cookies
    const getCsrfToken = () => {
      let csrfToken = null;
      if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(cookie => {
          if (cookie.trim().startsWith('csrftoken=')) {
            csrfToken = cookie.trim().split('=')[1];
          }
        });
      }
      return csrfToken;
    };
    
    // Set the CSRF token in the axios headers for all requests
    axios.defaults.headers.common['X-CSRFToken'] = getCsrfToken();
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        'http://localhost:8000/api/login/',
        { username, password },
        {
          withCredentials: true, // Ensure cookies are sent
        }
      );

      if (response.status === 200) {
        setMessage('Login successful!');
        // Handle successful login (e.g., redirect, update UI)
      }
    } catch (error) {
      setMessage('Login failed. Please check your credentials and try again.');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Login</button>
      <p>{message}</p>
    </form>
  );
};

export default Login;
