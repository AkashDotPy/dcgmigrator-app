import React, { useState } from 'react';
import {Link} from 'react-router-dom'

const SideNavbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleNavbar = () => {
    setIsOpen(!isOpen);
  }
  const handleMouseEnter = () => {
    setIsOpen(true);
  }

  const handleMouseLeave = () => {
    setIsOpen(false);
  }

  return (
    <div className={`bg-sky-600 h-screen ${isOpen ? 'w-64' : 'w-10'} transition-width duration-500 ease-in-out`}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}>
      <div className=''>
        <div className='flex justify-center text-4xl text-white cursor-pointer' onClick={toggleNavbar}>
          &#8801;
        </div>
      </div>
      <div className={`p-10 ${isOpen ? 'visible' : 'invisible'}`}>
        <div className='flex flex-col cursor-pointer text-white'>
          <div className='p-2 hover:bg-sky-700'>
            <Link to={'/'}>Home</Link>
          </div>
          <div className='p-2 hover:bg-sky-700'>
            <Link to={'/projecthome'}>Project Workspace</Link>
          </div>
          <div className='p-2 hover:bg-sky-700'>
            View Project
          </div>
          <div className='p-2 hover:bg-sky-700'>
          <Link to={'/listprojects'}>List project</Link>
          </div>
          <div className='p-2 hover:bg-sky-700'>
          <Link to={'/sourcemetadata'}>Source Meta Data</Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SideNavbar;
