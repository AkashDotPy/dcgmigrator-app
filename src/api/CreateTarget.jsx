import React, { useState } from 'react'
import axios from 'axios'

const CreateTarget = () => {
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
    } 
    catch (error) {
      setError(true)
    }
  }
    return (
      <div>
        <h1>Create Target</h1>
        <br />
        <form onSubmit={submitHandler}>
          <label>Project name:
            <input type="text"
                    name = "project_name"
                    value={requestData.project_name}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Database name:
            <input type="text"
                    name = "pg_dbname"
                    value={requestData.pg_dbname}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Hostname:
            <input type="text"
                    name = "pg_host"
                    value={requestData.pg_host}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Port:
            <input type="text"
                    name = "pg_port"
                    value={requestData.pg_port}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Username:
            <input type="text"
                    name = "pg_user"
                    value={requestData.pg_user}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Password:
            <input type="text"
                    name = "pg_password"
                    value={requestData.pg_password}
                    onChange = {handleInputChange} />
          </label>
          <br /><br />
          <label>Version:
            <input type="text"
                    name = "input_pg_version"
                    value={requestData.input_pg_version}
                    onChange = {handleInputChange} />
          </label>
          <br />
          <button type='submit'>Create target</button>
          <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            {responseData.Status && <p>{responseData.Status}</p>}
          </div>
        </form>
      </div>
    )
}

export default CreateTarget