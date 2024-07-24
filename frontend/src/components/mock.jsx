import React, { useState } from 'react';

const CreateProjectForm = () => {
  const [projectName, setProjectName] = useState('');
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errors = {};
    if (!projectName) errors.projectName = 'Project Name is required';
    if (!source) errors.source = 'Source is required';
    if (!target) errors.target = 'Target is required';
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    try {
      const response = await fetch('http://localhost:8000/createProject', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_name: projectName,
          source: source,
          target: target,
        }),
      });
      const data = await response.json();
      setMessage(data.message);
      setProjectName('');
      setSource('');
      setTarget('');
    } catch (error) {
      setMessage('An error occurred');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md w-full max-w-sm">
        <h2 className="text-2xl font-bold mb-4">Create Project</h2>
        
        <div className="mb-4">
          <label htmlFor="projectName" className="block text-gray-700">Project Name</label>
          <input
            type="text"
            id="projectName"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            className={`w-full px-3 py-2 border rounded ${errors.projectName ? 'border-red-500' : ''}`}
            placeholder="Enter project name"
          />
          {errors.projectName && <p className="text-red-500 text-sm">{errors.projectName}</p>}
        </div>

        <div className="mb-4">
          <label htmlFor="source" className="block text-gray-700">Source</label>
          <input
            type="text"
            id="source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className={`w-full px-3 py-2 border rounded ${errors.source ? 'border-red-500' : ''}`}
            placeholder="Enter source"
          />
          {errors.source && <p className="text-red-500 text-sm">{errors.source}</p>}
        </div>

        <div className="mb-4">
          <label htmlFor="target" className="block text-gray-700">Target</label>
          <input
            type="text"
            id="target"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            className={`w-full px-3 py-2 border rounded ${errors.target ? 'border-red-500' : ''}`}
            placeholder="Enter target"
          />
          {errors.target && <p className="text-red-500 text-sm">{errors.target}</p>}
        </div>

        <button
          type="submit"
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          Create Project
        </button>
        {message && <p className="mt-4 text-green-500">{message}</p>}
      </form>
    </div>
  );
};

export default CreateProjectForm;
