import React, {useState} from 'react';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <div className="relative bg-sky-600 p-4 md:p-10 flex items-center justify-between">
      <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg">
        <a href="https://www.datacloudgaze.com" target='_blank' rel="noopener noreferrer">
          <img src="https://static.wixstatic.com/media/5b8722_05a065ee3bee45428038293a3d45e92e~mv2.png/v1/fill/w_478,h_66,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/dcg_logo.png" alt="datacloudgaze" className="w-[300px] h-auto" />
        </a>
      </div>
      <ul className="md:flex hidden justify-end space-x-4">
        <li className="text-xl font-semibold text-white hover:text-gray-200 cursor-pointer border-r-2 border-gray-400 pr-6">
          <a href="https://www.datacloudgaze.com" target="_blank" rel="noopener noreferrer">About Us</a>
        </li>
        <li className="text-xl font-semibold text-white hover:text-gray-200 cursor-pointer border-r-2 border-gray-400 pr-6">
          <a href="https://www.datacloudgaze.com/post/extension-migration-assistance" target="_blank" rel="noopener noreferrer">Blogs</a>
        </li>
        <li
          className="text-xl font-semibold text-white hover:text-gray-200 cursor-pointer"
          onClick={() => document.getElementById('footer').scrollIntoView({ behavior: 'smooth' })}
        >
          Contact Us
        </li>
      </ul>
      <div className='md:hidden text-white text-4xl' onClick={toggleMenu}>
        <a href="#">&#8801;</a>
      </div>
      {isMenuOpen && (
        <div className="absolute top-full right-0 mt-2 w-full bg-sky-600 shadow-lg rounded-lg z-50 ">
          <ul className="flex flex-col items-center p-4 space-y-2 ">
            <li className="text-base font-semibold text-white hover:text-gray-200 cursor-pointer border-b-2 pb-2 border-b-gray-400" onClick={toggleMenu}>
              <a href="https://www.datacloudgaze.com" target="_blank" rel="noopener noreferrer">About Us</a>
            </li>
            <li className="text-base font-semibold text-white hover:text-gray-200 cursor-pointer border-b-2 pb-2 border-b-gray-400" onClick={toggleMenu}>
              <a href="https://www.datacloudgaze.com/post/extension-migration-assistance" target="_blank" rel="noopener noreferrer">Blogs</a>
            </li>
            <li
              className="text-base font-semibold text-white hover:text-gray-200 cursor-pointer"
              onClick={() => {
                document.getElementById('footer').scrollIntoView({ behavior: 'smooth' });
                setIsMenuOpen(false)
              }}
            >
              Contact Us
            </li>
          </ul>
      </div>
      )}
    </div>
  );
};

export default Navbar;
