import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RemoveProject = () => {
  const [projectName, setProjectName] = useState('');
  const [removeFile, setRemoveFile] = useState(false);
  const [dropTargetSchema, setDropTargetSchema] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const [responseData, setResponseData] = useState([])
  const [selectedProject, setSelectedProject] = useState([])

  useEffect(() => {
      (async() => {
          const response = await axios.get(`http://127.0.0.1:8000/projectname`)
          setResponseData(response.data.project_name)
          setProjectName(selectedProject)

      })()

  }, [selectedProject, projectName])
  // console.log(selectedProject)
  

  const handleSelectChange = (event) => {
      setSelectedProject(event.target.value)
    } 
    console.log(projectName)
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(false);
    // setProjectName(selectedProject)

    try {
      const response = await axios.post('http://127.0.0.1:8000/removeproject', {
        project_name: projectName,
        remove_file: removeFile,
        drop_target_schema: dropTargetSchema,
      });
      setResponseMessage(response.data.message);
    } catch (err) {
      setError(true);
      setResponseMessage('Error: Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center border shadow-md rounded-lg px-8 py-4 hover:bg-gray-200 hover:shadow-lg transition-transform transform hover:-translate-y-1">
      <form onSubmit={handleSubmit} className="">
        <h1 className="text-base font-semibold mb-2">Remove Project</h1>
        <div className="mb-2">
        {/* <label htmlFor="projects" className="block text-base font-semibold mb-2">Choose project:</label> */}

          <select
            id="projectName"
            value={selectedProject}
            onChange={handleSelectChange}
            className="block w-64 py-1 text-sm bg-white border border-gray-300"

          >
            <option value="" disabled>Select a project</option>
              {responseData.map((item, index) => (
                <option key={index} value={item}>
                  {item}
                </option>
              ))}
            </select>
        </div>
        <div className="mb-2 text-sm">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              className="form-checkbox"
              checked={removeFile}
              onChange={(e) => setRemoveFile(e.target.checked)}
            />
            <span className="ml-2">Remove all generated files</span>
          </label>
        </div>
        <div className="mb-2 text-sm">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              className="form-checkbox"
              checked={dropTargetSchema}
              onChange={(e) => setDropTargetSchema(e.target.checked)}
            />
            <span className="ml-2">Drop target schema</span>
          </label>
        </div>
        <div className="flex justify-between items-center text-base">
          <button
            type="submit"
            className={`py-1 px-4 bg-red-600 text-white rounded-lg ${
              loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={loading}
          >
            {loading ? 'Removing...' : 'Remove'}
          </button>
        </div>
        {responseMessage && (
          <div className={`mt-4 ${error ? 'text-red-500' : 'text-green-500'}`}>
            {responseMessage}
          </div>
        )}
      </form>
    </div>
  );
};

export default RemoveProject;
