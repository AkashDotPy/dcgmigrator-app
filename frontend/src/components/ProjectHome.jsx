import React, {useContext, useState} from 'react'
import { Link } from 'react-router-dom'
import Stepper from './Stepper'
import Breadcrumb from './Breadcrumb'
import SideNavbar from './SideNavbar'
import CreateProject from '../pages/CreateProject'
import CreateSource from '../pages/CreateSource'
import CreateTarget from '../pages/CreateTarget'
import Prerequisite from '../pages/Prerequisite'
import Convert from '../pages/Convert'
import PreDeploy from '../pages/PreDeploy'
import DataTransfer from '../pages/DataTransfer'
import PostDeploy from '../pages/PostDeploy'
import Validation from '../pages/Validation'
import SelectProject from './SelectProject'
import RemoveProject from '../pages/RemoveProject'
import ShowConfig from '../pages/ShowConfig';
import ListProjects from '../pages/ListProjects'
import ProjectContext from '../context/ProjectContext'

const ProjectHome = () => {
    const {createdProject} = useContext(ProjectContext)
    const [selectedProject, setSelectedProject] = useState("")
    const steps = [
        // { name: 'Create project', link: '/CreateProject', component: CreateProject},
        { name: 'Create Source', link: '/CreateSource', component:CreateSource },
        { name: 'Create Target', link: '/CreateTarget', component: CreateTarget },
        { name: 'Prerequisite', link: '/prerequisite', component: Prerequisite },
        { name: 'Convert', link: '/convert', component: Convert },
        { name: 'Pre-deploy', link: '/pre-deploy', component: PreDeploy},
        { name: 'Data transfer', link: '/data-transfer', component: DataTransfer },
        { name: 'Post-deploy', link: '/post-deploy', component: PostDeploy },
        { name: 'Validation', link: '/validation', component: Validation }
      ];
    
      const [currentStep, setCurrentStep] = useState(1);
    
      const handleNext = () => {
        setCurrentStep(prev => (prev < steps.length ? prev + 1 : prev));
        console.log(currentStep)
      }

      const CurrentPage = steps[currentStep - 1].component;

      const handleProjectChange = (e) => {
        setSelectedProject(e.target.value)            
      }
    
  return (
    <div>
        <div className='flex'>
          
            <div className='flex flex-col '>
                {/* <div className='flex'>
                </div> */}
                
                <div className='flex justify-between'>
                  <SelectProject/>
                  <RemoveProject/>
                  {/* <ShowConfig/> */}
                  <div className='flex flex-col'>
                  <div className=''>
                    <Link to={'/Projecthome/showconfig'}>Show config details</Link>
                  </div>
                  <div className=''>
                    <Link to={'/Projecthome/listprojects'}>List project</Link>
                  </div>
                  <div className=''>
                    <Link to={'/Projecthome/sourcemetadata'}>Source Meta Data</Link>
                  </div>
                  </div>
                  {/* <ListProjects/> */}
                </div>
                <div className='flex justify-center mt-10 font-semibold text-lg'>
                  <h1>Project : {createdProject}</h1>
                </div>
                <div>
                    <Stepper steps={steps} currentStep={currentStep} setCurrentStep={setCurrentStep} />
                </div>
                <div>
                    <Breadcrumb steps={steps} currentStep={currentStep} setCurrentStep={setCurrentStep} />
                </div>
                <div className='flex justify-center bg-slate-200 w-full h-full py-5'>
                    <CurrentPage/>
                </div>
                <div className='flex justify-between'>
                    <button  className="p-2 bg-sky-600 rounded-lg text-white w-20">
                      Back
                    </button>
                    <button  className="p-2 bg-sky-600 rounded-lg text-white w-20">
                      Edit
                    </button>
                    <button onClick={handleNext} className="p-2 bg-sky-600 rounded-lg text-white w-20">
                      Next
                    </button>
                </div>
            </div>
        </div>
    </div>
  )
}

export default ProjectHome