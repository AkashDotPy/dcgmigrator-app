import React from 'react'
import SelectProject from './SelectProject'
import CreateProject from '../pages/CreateProject'
import RemoveProject from '../pages/RemoveProject'

export default function Home() {
  return (
    <div className='flex justify-center items-center'>
      <CreateProject/>
      {/* <RemoveProject/> */}

    </div>
  )
}


