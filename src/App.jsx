import React, {useState} from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/navbar";
import About from "./components/About";
import CreateProject from "./api/CreateProject";
import ProjectName from "./api/ProjectName"
import CreateSource from "./api/CreateSource";
import CreateTarget from "./api/CreateTarget";
import ListProject from "./api/ListProject";
import ShowConfig from "./api/ShowConfig"
import SourceMetaData from "./api/SourceMetadata"
import Contact from "./components/Contact";
import Document from "./components/Document";

import Home from "./components/Home";
function App() {
  const [selectedProject, setSelectedProject] = useState('')
  return (
    <div className="container">
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/About" element={<About/>}/>
          <Route path="/Document" element={<Document/>}/>
          <Route path="/Contact" element={<Contact/>} />
          <Route path="/CreateProject" element={<CreateProject/>}/>
          <Route path = "/ViewProject" element = {<ProjectName
          selectedProject = {selectedProject}
          setSelectedProject = {setSelectedProject}/>} 
          />
          <Route path="/CreateSource" element={<CreateSource/>} />
          <Route path = "/createTarget" element = {<CreateTarget/>} />
          <Route path = "/ListProject" element = {<ListProject selectedProject = {selectedProject}/>} />
          <Route path = "/ShowConfig" element = {<ShowConfig selectedProject = {"testhr"}/>} />
          <Route path = "/SourceMetaData" element = {<SourceMetaData/>} />
        </Routes>
      </Router>
    </div>

  );
}

export default App;
