import { useState } from "react"
import ApiManager from "../utils/ApiManager";

function App (selectedProject) {
    const [showData, setShowData] = useState(false);
    const [data, error, loading] = ApiManager(`http://127.0.0.1:8000/showproject?project_name=${selectedProject}`);
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
        <header>
            <h2>Show config details</h2>
        </header>
          <button onClick={handleButtonClick}>Config details</button>
          {showData && (
            <div>
              <ul>
              <div>
                {data.map((item, index) => (
                  <li key={index}>
                    {`${Object.keys(item)[0]}: ${Object.values(item)[0]}`}
                  </li>
                ))}
              </div>
              </ul>
            </div>
          )}
        </div>
      );
}

export default App