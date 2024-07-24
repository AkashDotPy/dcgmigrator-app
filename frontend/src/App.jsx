import {BrowserRouter, Route, Routes} from "react-router-dom"
import Sidebar from "./components/Sidebar"

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route exact path="/" element={<Sidebar/>}></Route>
      </Routes>
      <Analytics />
    </BrowserRouter>
  )
}

export default App
