import React, { useState, useEffect } from 'react';
import ProjectContext from '../context/ProjectContext';

const ProjectContextProvider = ({ children }) => {
  const [createdProject, setCreatedProject] = useState(() => {
    const savedProject = localStorage.getItem('createdProject');
    return savedProject ? JSON.parse(savedProject) : null;
  });

  useEffect(() => {
    localStorage.setItem('createdProject', JSON.stringify(createdProject));
  }, [createdProject]);

  return (
    <ProjectContext.Provider value={{ createdProject, setCreatedProject }}>
      {children}
    </ProjectContext.Provider>
  );
};

export default ProjectContextProvider;