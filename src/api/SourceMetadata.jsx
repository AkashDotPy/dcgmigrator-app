import React, { useEffect, useState } from "react";
import ApiManager from "../utils/ApiManager";

function App() {
  const [showData, setShowData] = useState(false);
  const [schema, schemaError, schemaLoading] = ApiManager("http://127.0.0.1:8000/showschema");
  const [column, columnError, columnLoading] = ApiManager("http://127.0.0.1:8000/showcolumn");
  const [table, tableError, tableLoading] = ApiManager("http://127.0.0.1:8000/showtable");

  if (schemaError || columnError || tableError) {
    return <h1>Something went wrong</h1>;
  }

  if (schemaLoading || columnLoading || tableLoading) {
    return <h1>Loading...</h1>;
  }
  
  const handleButtonClick = () => {
    setShowData(true);
  };

  return (
    <div>
      <header>
        <h2>Source Meta Data</h2>
      </header>
      <a onClick={handleButtonClick}>View</a>
      {showData && (
        <div>
          <ul>
            <div>
              <li>
                <a href='#' onClick={handleButtonClick}>
                  show schema
                </a>
                {showData && (
                  <div>
                    <p>{schema}</p>
                  </div>
                )}
              </li>
              <li>
                <a href='#' onClick={handleButtonClick}>
                  show column
                </a>
                {showData && (
                  <div>
                    <p>{column}</p>
                  </div>
                )}
              </li>
              <li>
                <a href='#' onClick={handleButtonClick}>
                  show table
                </a>
                {showData && (
                  <div>
                    <p>{table}</p>
                  </div>
                )}
              </li>
            </div>
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
