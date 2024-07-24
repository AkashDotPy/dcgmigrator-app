import React, {useEffect, useState, useContext} from 'react'
import axios from 'axios'
import ProjectContext from '../context/ProjectContext'

const CreateTarget = () => {
  const {createdProject} = useContext(ProjectContext)
  const [responseData, setResponseData] = useState([])
  const [requestData, setRequestData] = useState({
    project_name : "",
    pg_dbname : "",
    pg_host : "",
    pg_port : "",
    pg_user : "",
    pg_password : "",
    input_pg_version : "",
  })

  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [isTargetCreated, setIsTargetCreated] = useState(false);

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
      setLoading(true)
      const response = await axios.post("http://127.0.0.1:8000/createTarget", requestData)
      setResponseData(response.data)
      setLoading(false)
      setIsTargetCreated(true)
    } 
    catch (error) {
      setError(true)
    }
  }
  console.log(createdProject)
  return (
    <div>
      <form onSubmit={submitHandler} className='bg-white p-8 rounded shadow-md w-[480px]'>
      <h1 className='text-xl font-semibold mb-5'>Create target</h1>
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
          <label htmlFor="pg_dbname" className="block text-gray-700">Database name</label>
          <input
            type="text"
            name="pg_dbname"
            value={requestData.pg_dbname}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.pgdbname && <span className='text-red-500 text-sm'>{errors.pgdbname}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="pg_host" className="block text-gray-700">Host name</label>
          <input
            type="text"
            name="pg_host"
            value={requestData.pg_host}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.pg_host && <span className='text-red-500 text-sm'>{errors.pg_host}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="pg_port" className="block text-gray-700">Port</label>
          <input
            type="text"
            name="pg_port"
            value={requestData.pg_port}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.pg_port && <span className='text-red-500 text-sm'>{errors.pg_port}</span>}  */}
          </div>
          <div className=''>
          <label htmlFor="pg_user" className="block text-gray-700">User name</label>
          <input
            type="text"
            name="pg_user"
            value={requestData.pg_user}
            onChange={handleInputChange}
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.pg_user && <span className='text-red-500 text-sm'>{errors.pg_user}</span>}  */}
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
          <label htmlFor="input_pg_version" className="block text-gray-700">Postgres version</label>
          <input
            type="text"
            name="input_pg_version"
            value={requestData.input_pg_version}
            onChange={handleInputChange}  
            className='py-1 px-3 text-sm border border-gray-300 rounded w-full'
          />
          {/* {errors.input_pg_version && <span className='text-red-500 text-sm'>{errors.input_pg_version}</span>}  */}
          </div>
        </div>
        <div className='mt-5'>
          <div className='flex gap-5'>
            <button type="submit"
                    className='py-1 px-4 bg-sky-600 text-white rounded-lg'>create</button>
            <button type="next"
                        className={`py-1 px-4 bg-sky-600 text-white rounded-lg ${
                          !isTargetCreated ? 'opacity-50 cursor-not-allowed' : ''
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

export default CreateTarget