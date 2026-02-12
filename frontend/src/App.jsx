import { useEffect } from "react";
import Camera from "./camera";

let lastSpoken = "";

function App() {

  // 🔊 Unlock audio (REQUIRED)
  const enableAudio = () => {
    const u = new SpeechSynthesisUtterance("Audio enabled");
    window.speechSynthesis.speak(u);
  };

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/detect");
        const data = await res.json();

        if (data.message && data.message !== lastSpoken) {
          const speech = new SpeechSynthesisUtterance(data.message);
          speech.rate = 1;
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(speech);
          lastSpoken = data.message;
        }
      } catch (e) {
        console.log("Waiting for backend...");
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Vision Assist</h2>
      <button onClick={enableAudio}>Enable Audio</button>
      <Camera />
    </div>
  );
}

export default App;
