import axios from 'axios'
import React from 'react'
import { Link } from 'react-router-dom'

const ShowConfig = ({selectedProject}) => {
  const handleChange = async () => {
    const response = await axios.get()
  }
  return (
    <div className=''>
      <Link to= '/projecthome/showconfig'>Show Config details{selectedProject}</Link>
    </div>
  )
}

export default ShowConfig