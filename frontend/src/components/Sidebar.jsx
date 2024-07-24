import React, { useState } from 'react';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className={`flex ${isOpen ? 'w-64' : 'w-16'} bg-gray-800 text-white h-screen transition-width duration-300`}>
      <div className="flex flex-col items-center justify-between h-full py-4">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="focus:outline-none"
        >
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={isOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16m-7 6h7'}
            />
          </svg>
        </button>
        <nav className="flex flex-col mt-10 space-y-4">
          <a href="#" className="flex items-center px-4 py-2 text-sm text-gray-300 rounded hover:bg-gray-700">
            Dashboard
          </a>
          <a href="#" className="flex items-center px-4 py-2 text-sm text-gray-300 rounded hover:bg-gray-700">
            Profile
          </a>
          <a href="#" className="flex items-center px-4 py-2 text-sm text-gray-300 rounded hover:bg-gray-700">
            Settings
          </a>
          <a href="#" className="flex items-center px-4 py-2 text-sm text-gray-300 rounded hover:bg-gray-700">
            Logout
          </a>
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;
