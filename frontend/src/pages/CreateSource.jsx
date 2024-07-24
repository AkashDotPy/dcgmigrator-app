import React, {useState, useContext, useEffect } from 'react'
import axios from 'axios'
import ProjectContext from '../context/ProjectContext'

const CreateSource = () => {
  const {createdProject} = useContext(ProjectContext)
  const [responseData, setResponseData] = useState([])
  const [requestData, setRequestData] = useState({
    project_name : "",
    home : "", 
    host : "",
    service_name : "",
    port : "",
    user : "",
    password : "",
    ora_schema : "",
  })

  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isSourceCreated, setIsSourceCreated] = useState(false);

  useEffect(() => {
    if (createdProject) {
      setRequestData(prevState => ({
        ...prevState,
        project_name: createdProject,
      }));
    }
  }, [createdProject]);

  const handleInputChange = (e) => {
    const{ name, value } = e.target
    setRequestData((prevData) => ({
      ...prevData,
      [name] : value,
    }))

  }
  const submitHandler = async(e) => {
    e.preventDefault()
    try {
      setError(false)
      setLoading(true)
      const response = await axios.post("http://127.0.0.1:8000/createSource", requestData)
      setResponseData(response.data)
      setLoading(false)
      setIsSourceCreated(true)
    } 
    catch (error) {
      setLoading(false)
      setError(true)
    }
  }
  console.log(requestData)
  return (
    <div>
      <form onSubmit={submitHandler} className='bg-white p-8 rounded shadow-md w-[480px]'>
      <h1 className='text-xl font-semibold mb-5'>Create Source</h1>
        <div className='grid grid-cols-2 gap-4'>
          <div className=''>
          <label htmlFor="project_name" className="block text-gray-700">Project Name</label>
          <input
            type="text"
            name="project_name"
            value={createdProject} 
            onChange={handleInputChange}
            disabled={true}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.project_name && <span className='text-red-500 text-sm'>{errors.project_name}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="home" className="block text-gray-700">Oracle home (optional)</label>
          <input
            type="text"
            name="home"
            value={requestData.home}
            // defaultValue={requestData.home}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.home && <span className='text-red-500 text-sm'>{errors.home}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="host" className="block text-gray-700">Host name</label>
          <input
            type="text"
            name="host"
            value={requestData.host}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.host && <span className='text-red-500 text-sm'>{errors.host}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="servicename" className="block text-gray-700">Service name</label>
          <input
            type="text"
            name="service_name"
            value={requestData.service_name}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.service_name && <span className='text-red-500 text-sm'>{errors.service_name}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="port" className="block text-gray-700">Port</label>
          <input
            type="text"
            name="port"
            value={requestData.port}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.port && <span className='text-red-500 text-sm'>{errors.port}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="username" className="block text-gray-700">User name</label>
          <input
            type="text"
            name="user"
            value={requestData.user}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.username && <span className='text-red-500 text-sm'>{errors.username}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="password" className="block text-gray-700">Password</label>
          <input
            type="text"
            name="password"
            value={requestData.password}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.password && <span className='text-red-500 text-sm'>{errors.password}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="oraschema" className="block text-gray-700">Schema</label>
          <input
            type="text"
            name="ora_schema"
            value={requestData.ora_schema}
            onChange={handleInputChange}  
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.ora_schema && <span className='text-red-500 text-sm'>{errors.ora_schema}</span>}  */}
          </div>
        </div>
        <div className='mt-5'>
          <div className='flex gap-5'>
            <button type="submit"
                    className='py-1 px-4 bg-sky-600 text-white rounded-lg'>Create</button>
            <button type="next"
                    className={`py-1 px-4 bg-sky-600 text-white rounded-lg ${
                      !isSourceCreated ? 'opacity-50 cursor-not-allowed' : ''
                    }`}>Next</button>
            
          </div>
          <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            {responseData.Status && <p>{responseData.Status}</p>}
          </div>
        </div>
  
      </form>
    </div>
  )
}

export default CreateSource