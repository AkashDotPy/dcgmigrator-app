
import ApiManager from "../utils/ApiManager";

function ProjectName ({selectedProject, setSelectedProject}){
    const [data, error, loading] = ApiManager("http://127.0.0.1:8000/projectname");
    
    if (error) {
      return <h1>Something went wrong</h1>;
    }
  
    if (loading) {
      return <h1>Loading...</h1>;
    }
    
    const handleSelectChange = (event) => {
      setSelectedProject(event.target.value)
      
    }    
    return (
        <div>
            <header>
                <h2>Project Name</h2>
            </header>
          
          <select value = {selectedProject} onChange={handleSelectChange}>
            {data.map((item, index) => (
              <option key={index} value={item.Project_name}>
                {item.Project_name}
              </option>
            ))}
          </select>
          {selectedProject && (
            <p>You have selected : {selectedProject}</p>
          )}
        </div>
      );
      
}


export default ProjectName