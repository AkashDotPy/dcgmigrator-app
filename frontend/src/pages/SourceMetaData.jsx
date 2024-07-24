import axios from 'axios'
import React, { useEffect, useState } from 'react'

function SourceMetaData() {
  const [schemaData, setSchemaData] = useState([])
  const [columnData, setColumnData] = useState([])
  const [tableData, setTableData] = useState([])
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    (async() => {
      try {
        setLoading(true)
        const schemaResponse = await axios.get("http://127.0.0.1:8000/showschema")
        const columnResponse = await axios.get("http://127.0.0.1:8000/showcolumn")
        const tableResponse = await axios.get("http://127.0.0.1:8000/showtable")
        setSchemaData(schemaResponse.data)
        setColumnData(columnResponse.data)
        setTableData(tableResponse.data)
        setLoading(false)
      } catch (error) {
        setError(true)
        setLoading(false)
      }
    })()
  }, [])
  
  return (
    <div>
      <div>
        <h1>Schema Data</h1>
        <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            
          </div>
        {schemaData}
      </div>
      <div>
      <h1>Column Data</h1>
      <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            
          </div>
        {columnData}
      </div>
      <div>
      <h1>Table Data</h1>
      <div>
            {loading && <p>Loading...</p>}
            {error && <p>Error: Something went wrong.</p>}
            
          </div>
        {tableData}
      </div>
    </div>
  )
}

export default SourceMetaData