import { useState, useEffect } from 'react'
import axios from 'axios';
import './App.css'
import Recording from './Recording';


function App() {
  const [data, setData] = useState("")
  const [result, setresult] = useState()  

  // const getMembers = async () => {
  //   const res = await axios.post("http://localhost:5000/members")
  //   setData(res.data);
  //   console.log(result);
  // }

  // const getresemblyzer = async () => {
  //   const res = await axios.post("http://localhost:5000/resemblyzer")
  //   setresult(res.data)
  //   console.log(result)
  // }

  return (    
    <>
      <div className="body">
        <h1>Welcome</h1>
        <Recording></Recording>
      </div>
    </>
  )
}

export default App
