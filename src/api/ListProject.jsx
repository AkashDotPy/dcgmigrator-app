import { useState } from "react";
import ApiManager from "../utils/ApiManager";;
 
function App({selectedProject}){
  const [showData, setShowData] = useState(false)
  const [data, error, loading] = ApiManager(`http://127.0.0.1:8000/showproject?project_name=${selectedProject}`);
  
  console.log(data)
  
  if (error) {
    return <h1>Something went wrong</h1>;
  }

  if (loading) {
    return <h1>Loading...</h1>;
  }

  const handleButtonClick = () =>{
    setShowData(true)
  }

  return (
    <div>
      <header><h2>Project details list</h2></header>
      <button onClick={handleButtonClick}>Project details</button>
      { showData &&(
        <table>
          <thead>
            <tr>
              <th>Project_name</th>
              <th>date_created</th>
              <th>status</th>
              <th>source</th>
              <th>target</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, index) => (
              <tr key={index}>
                <td>{item.project_name}</td>
                <td>{item.date_created}</td>
                <td>{item.status}</td>
                <td>{item.source}</td>
                <td>{item.target}</td>
              </tr>
            ))}
          </tbody>
          
        </table>
        )}
        {selectedProject && (
            <p>You have selected : {selectedProject}</p>
          )}

    </div>
  );
  }
export default App