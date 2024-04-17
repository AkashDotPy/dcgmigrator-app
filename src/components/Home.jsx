import React from 'react'
import cloudImage from '../assessts/cloud.jpeg';
import '../styles/Home.css';

function Home() {
    return (
        <div className="home-container">
          <h1 className="welcome-text">Welcome to the world of database migration</h1>
          <img className="cloud-image" src={cloudImage} alt="cloud" />
        </div>
      )
    }

export default Home