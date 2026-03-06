import { useState } from "react";
import Camera from "./camera";
import "./App.css";

function App() {

  const [mode, setMode] = useState(null);

  const speak = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(speech);
  };

  if (!mode) {
    return (
      <div className="container">

        <h1 className="title">Vision Assist</h1>

        <div className="card-container">

          <div
            className="card"
            onMouseEnter={() => speak("Object Detection")}
            onClick={() => setMode("object")}
          >
            <h3>Object Detection</h3>
          </div>

          <div
            className="card"
            onMouseEnter={() => speak("Currency Detection")}
            onClick={() => setMode("currency")}
          >
            <h3>Currency Detection</h3>
          </div>

        </div>

      </div>
    );
  }

  return (
    <div className="container">

      <button
        onMouseEnter={() => speak("Back to Home")}
        onClick={() => setMode(null)}
      >
        Back to Home
      </button>

      <h2>
        {mode === "object" ? "Object Detection" : "Currency Detection"}
      </h2>

      <Camera mode={mode} />

    </div>
  );
}

export default App;