import React from 'react';
import { FaYoutube, FaLinkedin } from 'react-icons/fa';
import { RiTwitterXFill } from 'react-icons/ri';

const Footer = () => {
  return (
    <footer id="footer" className="bg-sky-600 text-white py-4">
        <div className='flex items-center justify-end px-2'>
          <div className="flex flex-col sm:mr-2">
            <div>
              <h5 className="sm:text-sm lg:text-base font-semibold">Report Issue/Contact Us</h5>
              <p className='sm:text-xs lg:text-sm'>contact@datacloudgaze.com</p>
            </div>
            <div>
              <h5 className="sm:text-sm lg:text-base font-semibold py-2">Follow Us</h5>
              <div className="flex items-center space-x-10">
                <a href="https://www.linkedin.com/company/datacloudgaze-consulting" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                  <div className="bg-white p-2 rounded-full">
                        <FaLinkedin className="text-2xl text-slate-700 hover:text-blue-600" />
                  </div>
                </a>
                <a href="https://x.com/datacloudgaze" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                    <div className="bg-white p-2 rounded-full">
                        <RiTwitterXFill className="text-2xl text-slate-700 hover:text-gray-800" />
                    </div>
                </a>
                <a href="www.youtube.com/@datacloudgaze" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                    <div className="bg-white p-2 rounded-full">
                        <FaYoutube className="text-2xl text-slate-700 hover:text-red-600" />
                  </div>
                </a>
              </div>
            </div>
            </div>
            </div>
      <div className="flex justify-center text-sm text-white text-center md:text-left mt-4">
          &copy; {new Date().getFullYear()} DataCloudGaze Consulting. All rights reserved.
        </div>
    </footer>
  );
};

export default Footer;
