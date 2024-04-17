import { useState } from "react"


function Increment(){
   
    const [counter, setCounter] = useState(10)
    
    const addValue = () =>{
        if (counter < 20){
            setCounter(counter+1)
        }
    }

    const removeValue = () =>{
        if (counter > 0){
            setCounter(counter-1)
        }
    }


    return (
        <div>
            <h1>Counter</h1>
            <button onClick={addValue}>Add value{counter}</button>
            <br />
            <br />
            <button onClick={removeValue}>Remove value{counter}</button>
        </div>
    )
}

export default Increment