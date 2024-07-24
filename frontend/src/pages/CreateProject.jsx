import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import ProjectContext from '../context/ProjectContext';

const CreateProject = () => {
  const {createdProject, setCreatedProject} = useContext(ProjectContext)
  const [responseData, setResponseData] = useState([]);
  const [requestData, setRequestData] = useState({
    project_name: '',
    source: '',
    target: '',
  });
  const [error, setError] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [isProjectCreated, setIsProjectCreated] = useState(false);
  const [options, setOptions] = useState({ sources: [], targets: [] });

  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:8000/createProject?fetch_options=true');
        setOptions(response.data);
      } catch (error) {
        setError(true);
      }
    };
    fetchOptions();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRequestData((prevData) => ({
      ...prevData,
      [name]: value,

    }));
  }

  const validateInput = () => {
    const validationErrors = {};
    if (!requestData.project_name.trim()) {
      validationErrors.project_name = 'Project name is required';
    }
    if (!requestData.source.trim()) {
      validationErrors.source = 'Source is required';
    }
    if (!requestData.target.trim()) {
      validationErrors.target = 'Target is required';
    }
    setErrors(validationErrors);
    return validationErrors;
  };

  const submitHandler = async (e) => {
    e.preventDefault();
    if (Object.keys(validateInput()).length === 0) {
      try {
        setLoading(true);
        setError(false);

        const response = await axios.post('http://127.0.0.1:8000/createProject', requestData);
        setResponseData(response.data);
        setLoading(false);
        if (response.data.Status === "project is created successfully") {
          setIsProjectCreated(true);
          setCreatedProject(requestData.project_name);
        }

      } catch (error) {
        setError(true);
        setIsProjectCreated(false)
      } finally {
        setLoading(false);
      }
    }
  };

  console.log(createdProject)
  const handleNext = () => {
    <Link to={"/projecthome"}></Link>
  }

  return (
    <div className='flex items-center justify-center min-h-screen'>
      <form onSubmit={submitHandler} className='bg-white p-5 rounded border shadow-lg w-[480px]'>
        <h1 className='text-xl font-semibold mb-5'>Create Project</h1>
        <div className='mb-4'>
          <label htmlFor='projectName' className='block text-gray-700'>Project Name</label>
          <input
            type='text'
            name='project_name'
            value={requestData.project_name}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500'
            placeholder='Enter project name'
          />
          {errors.project_name && <span className='text-red-500 text-sm'>{errors.project_name}</span>}
        </div>
        <div className='mb-4'>
          <label htmlFor='source' className='block text-gray-700'>
            Source
          </label>
          <select
            name='source'
            value={requestData.source}
            onChange={handleInputChange}
            className='block w-full py-1 px-3 text-sm border border-gray-300 rounded bg-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500'
          >
            <option value='' disabled>Select source</option>
            {options.sources.map((source) => (
              <option key={source} value={source}>{source}</option>
            ))}
          </select>
          {errors.source && <span className='text-red-500 text-sm'>{errors.source}</span>}
        </div>
        <div className='mb-4'>
          <label htmlFor='target' className='block text-gray-700'>
            Target
          </label>
          <select
            name='target'
            value={requestData.target}
            onChange={handleInputChange}
            className='block w-full py-1 px-3 text-sm border border-gray-300 rounded bg-white placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500'
          >
            <option value='' disabled>Select target</option>
            {options.targets.map((target) => (
              <option key={target} value={target}>{target}</option>
            ))}
          </select>
          {errors.target && <span className='text-red-500 text-sm'>{errors.target}</span>}
        </div>
        <div className='flex gap-5 mt-5'>
          <div>
            <button type='submit' 
                    className='py-1 px-4 bg-blue-600 text-white rounded-lg'>
              Create
            </button>
          </div>
          <div>
            <Link to={"/projecthome"}>
              <button
                type='button'
                className={`py-1 px-4 bg-blue-600 text-white rounded-lg ${
                  !isProjectCreated ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                disabled={!isProjectCreated}
              >
                Next
              </button>
            </Link>
          </div>
        </div>
        <div>
          {loading && <p>Loading...</p>}
          {error && <p>Error: Something went wrong.</p>}
          {responseData.Status && <p>{responseData.Status}</p>}
        </div>
      </form>
    </div>
  );
};

export default CreateProject;
