import { useState, useEffect } from "react";

let lastTimeSpoken = 0;

function Camera({ mode }) {

  const [audioEnabled, setAudioEnabled] = useState(false);

  const speak = (text) => {
    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(speech);
  };

  const enableAudio = () => {
    const u = new SpeechSynthesisUtterance("Audio enabled");
    window.speechSynthesis.speak(u);
    setAudioEnabled(true);
  };

  const disableAudio = () => {
    window.speechSynthesis.cancel();
    setAudioEnabled(false);
  };

  const videoURL =
    mode === "object"
      ? "/video/object"
      : "/video/currency";

  useEffect(() => {

    const interval = setInterval(async () => {

      if (!audioEnabled) return;

      try {

        const res = await fetch(`/detect/${mode}`);
        const data = await res.json();

        if (data.message) {

          const now = Date.now();

          if (now - lastTimeSpoken > 3000) {

            const speech = new SpeechSynthesisUtterance(data.message);
            speech.rate = 1;

            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(speech);

            lastTimeSpoken = now;
          }
        }

      } catch (e) {
        console.log("Waiting for backend...");
      }

    }, 1000);

    return () => clearInterval(interval);

  }, [audioEnabled, mode]);

  return (
    <div>

      <button
        onMouseEnter={() => speak("Enable Audio")}
        onClick={enableAudio}
      >
        Enable Audio
      </button>

      <button
        onMouseEnter={() => speak("Disable Audio")}
        onClick={disableAudio}
      >
        Disable Audio
      </button>

      <br /><br />

      <img
        src={videoURL}
        width="720"
        alt="camera"
      />

    </div>
  );
}

export default Camera;