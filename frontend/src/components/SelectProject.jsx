import axios from 'axios';
import React, { useContext, useEffect, useState } from 'react';
import ProjectContext from '../context/ProjectContext';

function SelectProject() {
    const { createdProject, setCreatedProject } = useContext(ProjectContext);
    const [responseData, setResponseData] = useState([]);
    const [selectedProject, setSelectedProject] = useState('');

    useEffect(() => {
        (async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/projectname');
                setResponseData(response.data.project_name);
            } catch (error) {
                console.error("Error fetching project names:", error);
            }
        })();
    }, []);

    const handleSelectChange = (event) => {
        const project = event.target.value;
        setSelectedProject(project);
        setCreatedProject(project);  // Update the context state
    };

    return (
        <div className="">
            <div className='border bg-white shadow-md rounded-lg px-8 py-4 hover:bg-gray-200 hover:shadow-lg transition-transform transform hover:-translate-y-1'>
                <label htmlFor="projects" className="block text-base font-semibold mb-2">Choose project:</label>
                <select
                    id="projects"
                    value={selectedProject}
                    onChange={handleSelectChange}
                    className="block w-64 py-1 text-sm bg-white border border-gray-300 focus:outline-none focus:ring-1 focus:ring-sky-600 focus:border-sky-500"
                >
                    <option value="" disabled>Select a project</option>
                    {responseData.map((item, index) => (
                        <option key={index} value={item}>
                            {item}
                        </option>
                    ))}
                </select>
            </div>
            <div>
                {selectedProject && (
                    <p className="mt-4 text-base text-gray-700">You have selected: <span className="font-semibold">{selectedProject}</span></p>
                )}
            </div>
        </div>
    );
}

export default SelectProject;
