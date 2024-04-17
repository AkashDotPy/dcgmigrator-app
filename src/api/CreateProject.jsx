import React, { useState } from 'react';
import axios from 'axios';

const App = () => {
  const [responseData, setResponseData] = useState([]);
  const [requestData, setRequestData] = useState({
    project_name: '',
    source: '',
    target: '',
  });
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRequestData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const submitHandler = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(false);

      const response = await axios.post('http://127.0.0.1:8000/createProject', requestData);
      setResponseData(response.data);

    } catch (error) {
      setError(true);

    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Create Project</h1>
      <form onSubmit={submitHandler}>
        <label>
          Project Name:
          <input
            type="text"
            name="project_name"
            value={requestData.project_name}
            onChange={handleInputChange}
          />
        </label>
        <br /><br />
        <label>
          Source:
          <input
            type="text"
            name="source"
            value={requestData.source}
            onChange={handleInputChange}
          />
        </label>
        <br /><br />
        <label>
          Target:
          <input
            type="text"
            name="target"
            value={requestData.target}
            onChange={handleInputChange}
          />
        </label>
        <br />
        <button type="submit">Create Project</button>
        <div>
          {loading && <p>Loading...</p>}
          {error && <p>Error: Something went wrong.</p>}
          {responseData.Status && <p>{responseData.Status}</p>}
        </div>
      </form>
    </div>
  );
};

export default App;
