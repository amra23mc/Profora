import { useVoiceVisualizer, VoiceVisualizer } from "react-voice-visualizer-react19";
import { useState, useEffect } from 'react'
import axios from 'axios';

export default function Recording() {
  // Initialize controls
  const recorderControls = useVoiceVisualizer();
  const { recordedBlob } = recorderControls;

  const playbackControls = useVoiceVisualizer();
  const { setPreloadedAudioBlob } = playbackControls;

  const [result, setresult] = useState()  
  const [text, setText] = useState()

  // Automatically triggers once on initial page load
  useEffect(() => {
    getText();
  }, []); // Empty brackets ensure this only fires once when the component mounts


  const getText = async () => {
    const res = await axios.post("http://localhost:5000/text")
    setText(res.data)

    getAudio()
  }

  const getAudio = async () => {
      try {
        const res = await axios.post("http://localhost:5000/sendAudio", {}, {
          responseType: "blob", 
        });
      
        setPreloadedAudioBlob(res.data);
      
      } catch (err) {
        console.error("Error communicating with backend:", err);
      }
  }

  const getresemblyzer = async () => {
    if(!recordedBlob) return;

    const audioFile = new File([recordedBlob], "audio.webm", {
      type: recordedBlob.type || "audio/webm", 
      lastModified: Date.now(),
    });

    const formData = new FormData();
    formData.append("audioFile", audioFile)

    const res = await axios.post("http://localhost:5000/resemblyzer", formData)
    setresult(res.data)
    console.log(result)
  }

  return (
    <div className="column" style={{ backgroundColor: "#1e1e24", padding: "20px", borderRadius: "8px" }}>
      <div className="row">
        <h3 style={{ color: "aliceblue" }}>Say: "{text}"</h3>
        <button type='button' className='button btn-gradient btn btn-primary' onClick={getText}>Next</button>
      </div>

      <VoiceVisualizer controls={playbackControls} isControlPanelShown={true}></VoiceVisualizer>
      {/* <button type='button' className='button btn-gradient btn btn-primary' onClick={getAudio}>Generate</button> */}
      
      
      <VoiceVisualizer controls={recorderControls} />
      <div>
          <button type='button' className='button btn-gradient btn btn-primary' onClick={getresemblyzer}>Calculate</button>
          <p>Accuracy: {result}%</p>
      </div>
    </div>
  );
}
