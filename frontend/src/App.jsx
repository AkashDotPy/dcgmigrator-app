import 'tailwindcss/tailwind.css';
import {BrowserRouter, Route, Routes} from "react-router-dom"
import  Home  from './components/Home';
import ShowConfig from './pages/ShowConfig';
import ProjectHome from './components/ProjectHome';
import SourceMetaData from './pages/SourceMetaData';
import ListProjects from './pages/ListProjects';
import SelectProject from './components/SelectProject';
import Navbar from './components/Navbar'
import SideNavbar from './components/SideNavbar';
import Footer from './components/Footer'
import { Component, useState } from 'react';
import ProjectContextProvider from './context/ProjectContextProvider';
import NavBreadcrumb from './components/NavBreadcrumb'

const App = () => {
  const [selectedProject, setSelectedProject] = useState([])
  return (
    <BrowserRouter>
      <ProjectContextProvider>
      <Navbar/>
      <div className='flex'>
        <SideNavbar/>
        
        <div className='p-10'>
        <NavBreadcrumb/>
          {/* <div className='flex '>
          <SelectProject/>
          <ShowConfig selectedProject={selectedProject}/>
          </div> */}
          
          <Routes>
            <Route exact path="/" element={<Home/>}></Route>
            <Route exact path="/Projecthome" element={<ProjectHome/>}></Route>
            <Route exact path="/Projecthome/showconfig" element={<ShowConfig/>}></Route>
            <Route exact path="/Projecthome/sourcemetadata" element={<SourceMetaData/>}></Route>
            <Route exact path="/Projecthome/listprojects" element={<ListProjects/>}></Route>
          </Routes>
        </div>
      </div>
      <Footer/>
      </ProjectContextProvider>
    </BrowserRouter>
  )
}

export default App;
