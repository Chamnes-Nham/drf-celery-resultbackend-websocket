import React, { useEffect, useState } from 'react';
import axios from 'axios';

const App = () => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');

  useEffect(() => {
    // Fetch initial comments
    axios.get('http://127.0.0.1:8000/api/comments/').then((response) => {
      setComments(response.data);
    });

    // WebSocket connection
    const ws = new WebSocket('ws://127.0.0.1:8000/ws/comments/');
    ws.onmessage = (event) => {
      const comment = JSON.parse(event.data);
      setComments((prev) => [comment, ...prev]);
    };

    return () => ws.close();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (newComment.trim()) {
      await axios.post('http://127.0.0.1:8000/api/comments/', { content: newComment });
      setNewComment('');
    }
  };

  return (
    <div>
      <h1>Comments</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
        />
        <button type="submit">Post</button>
      </form>
      <ul>
        {comments.map((comment, index) => (
          <li key={index}>{comment.content}</li>
        ))}
      </ul>
    </div>
  );
};

export default App;
