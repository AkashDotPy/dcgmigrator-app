import React from 'react';
import { Link } from 'react-router-dom'
import '../styles/navbar.css';

const Navbar = () => {

  return (
    <div className="navbar">
      <div className="logo">
        <h1>DCGmigrator</h1>
      </div>
      <nav>
        <ul>
          <li><Link to="/">Home</Link></li>
          <li><a href="#">Migration</a>
            <ul className='dropdown'>
              <li><Link to="/CreateProject">Create Project</Link></li>
              <li><Link to="/ViewProject">View Project</Link></li>
              <li><Link to = "/CreateSource">Create Source</Link></li>
              <li><Link to ="/CreateTarget">Create Target</Link></li>
              <li><Link to = "/ListProject">List Project</Link></li>
              <li><Link to = "/ShowConfig">Show Config</Link></li>
              <li><Link to = "/SourceMetaData">Source Meta Data</Link></li>
            </ul>
          </li>
          <li><Link to="/About">About</Link></li>
          <li><Link to="/Document">Document</Link></li>
          <li><Link to="/Contact">Contact</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default Navbar;