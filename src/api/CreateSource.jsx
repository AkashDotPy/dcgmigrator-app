import React, { useState } from 'react'
import axios from 'axios'

const CreateSource = () => {
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
      const response = await axios.post("http://127.0.0.1:8000/createSource", requestData)
      setResponseData(response.data)
      setLoading(false)
    } 
    catch (error) {
      setError(true)
    }

  }
    return (
      <div>
        <h1>Create Source</h1>
        <br /><br />
        <form onSubmit={submitHandler}>
          <label>Project Name:
            <input type="text"
                    name ="project_name"
                    value = {requestData.project_name}
                    onChange={handleInputChange}    
            />
          </label>
          <br /><br />
          <label> Oracle user:
            <input type="text"
                    name = "user"
                    value = {requestData.user}
                    onChange={handleInputChange}
                    
            />
            </label>
            <br /><br />
            <label>Password:
            <input type="text"
                    name = "password"
                    value = {requestData.password}
                    onChange={handleInputChange}
                    
            />
          </label>
          <br /><br />
          <label>Hostname:
            <input type="text"
                    name = "host"
                    value = {requestData.host}
                    onChange={handleInputChange}
                   
            />
          </label>
          <br /><br />
          <label>Service name:
            <input type="text"
                    name = "service_name"
                    value = {requestData.service_name}
                    onChange={handleInputChange}
                     
            />
          </label>
          <br /><br />
          <label> Port:
            <input type="text"
                    name = "port"
                    value = {requestData.port}
                    onChange={handleInputChange}
                 
            />
          </label>
          <br /><br />
          <label> Oracle home:
            <input type="text"
                    name = "home"
                    value = {requestData.home}
                    onChange={handleInputChange}
                 
            />
          </label>
          <br /><br />
          <label>Schema:
            <input type="text"
                    name = "ora_schema"
                    value = {requestData.ora_schema}
                    onChange={handleInputChange}
            />
          </label>
          <br />
          <button type="submit">Create Source</button>
          <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            {responseData.Status && <p>{responseData.Status}</p>}
          </div>
        </form>
      </div>
    )
}

export default CreateSource