import React, { useEffect, useState } from 'react'
import axios from 'axios'

function ListProjects() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)
  const [projectDetails, setProjectDetails] = useState([])

  useEffect(() => {
    (async () => {
      try {
        setLoading(true)
        setError(false)

        const response = await axios.get('http://127.0.0.1:8000/listProjects')
        setProjectDetails(response.data)
      } catch (error) {
        setError(true)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) {
    return <div>Loading...</div>
  }

  if (error) {
    return <div>Error: Something went wrong.</div>
  }

  if (projectDetails.length === 0) {
    return <div>No projects found.</div>
  }

  const headers = Object.keys(projectDetails[0])
  const rows = projectDetails.map(item => Object.values(item))

  return (
    <div className=''>
      {/* <h1>List of Projects</h1> */}
      <table className="table-auto w-full border border-gray-300">
        <thead className="bg-sky-600">
          <tr>
            {headers.map((header, idx) => (
              <th key={idx} className="py-2 px-4 text-white font-semibold border border-gray-300">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, idx) => (
            <tr key={idx} className={idx % 2 === 0 ? 'bg-gray-100' : 'bg-white'}>
              {row.map((cell, cellIdx) => (
                <td
                  key={cellIdx}
                  className="text-center py-2 px-4 border border-gray-300"
                >
                  <div className='flex justify-center'>{cell}</div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ListProjects
