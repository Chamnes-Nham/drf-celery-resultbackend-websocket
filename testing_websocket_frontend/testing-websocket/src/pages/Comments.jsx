// import React, { useEffect, useState } from 'react';
// import axios from 'axios';

// const Comments = () => {
//   const [comments, setComments] = useState([]);
//   const [newComment, setNewComment] = useState('');

//   useEffect(() => {
//     // Fetch initial comments
//     axios.get('http://127.0.0.1:8000/api/comments/').then((response) => {
//       setComments(response.data);
//     });

//     // WebSocket connection
//     const ws = new WebSocket('ws://127.0.0.1:8000/ws/comments/');
//     ws.onmessage = (event) => {
//       const comment = JSON.parse(event.data);
//       setComments((prev) => [comment, ...prev]);
//     };

//     return () => ws.close();
//   }, []);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     if (newComment.trim()) {
//       await axios.post('http://127.0.0.1:8000/api/comments/', { content: newComment }, { withCredentials: true } );
//       setNewComment('');
//     }
//   };

//   return (
//     <div>
//       <h1>Comments</h1>
//       <form onSubmit={handleSubmit}>
//         <input
//           type="text"
//           value={newComment}
//           onChange={(e) => setNewComment(e.target.value)}
//           placeholder="Write a comment..."
//         />
//         <button type="submit">Post</button>
//       </form>
//       <ul>
//         {comments.map((comment, index) => (
//           <li key={index}>{comment.content}</li>
//         ))}
//       </ul>
//     </div>
//   );
// };

// export default Comments;



import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Comments = () => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Fetch initial comments
    axios.get('http://127.0.0.1:8000/api/comments/', { withCredentials: true })
      .then((response) => {
        setComments(response.data);
      })
      .catch(error => {
        console.error('Error fetching comments:', error);
        setMessage('Failed to load comments.');
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
      try {
        const response = await axios.post(
          'http://127.0.0.1:8000/api/comments/',
          { content: newComment },
          { withCredentials: true }
        );
        
        setNewComment('');
        setMessage('Comment posted, awaiting task completion.');
        checkTaskStatus(response.data.task_id);
      } catch (error) {
        console.error('Error posting comment:', error);
        setMessage('Failed to post comment. Please try again.');
      }
    }
  };

  const checkTaskStatus = async (task_id) => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/api/task-status/${task_id}/`, { withCredentials: true });
      if (response.data.status === 'SUCCESS') {
        setMessage('Comment posted successfully!');
      } else {
        setMessage('Comment is still being processed.');
      }
    } catch (error) {
      console.error('Error checking task status:', error);
      setMessage('Failed to check task status.');
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
      {message && <p>{message}</p>}
      <ul>
        {comments.map((comment, index) => (
          <li key={index}>{comment.content}</li>
        ))}
      </ul>
    </div>
  );
};

export default Comments;
