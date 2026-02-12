from flask import Flask, Response, send_from_directory, jsonify
from flask_cors import CORS
import cv2
import time
from ultralytics import YOLO

# ---------------- APP SETUP ----------------

app = Flask(
    __name__,
    static_folder="../frontend/dist",
    static_url_path=""
)

CORS(app)

# ---------------- LOAD YOLO ----------------

MODEL_PATH = "yolov8n.pt"   # SAME FOLDER as app.py
model = YOLO(MODEL_PATH)

# ---------------- CAMERA -------------------

cap = cv2.VideoCapture(0)

latest_message = ""
last_spoken_message = ""
last_spoken_time = 0

SPEECH_DELAY = 3   # seconds between announcements

# ---------------- POSITION LOGIC -----------

def get_position(x_center, frame_width):
    if x_center < frame_width / 3:
        return "on your left"
    elif x_center > 2 * frame_width / 3:
        return "on your right"
    else:
        return "ahead"

# ---------------- VIDEO STREAM -------------

def generate_frames():
    global latest_message, last_spoken_message, last_spoken_time

    while True:
        success, frame = cap.read()

        if not success:
            break

        results = model(frame, stream=True)

        frame_width = frame.shape[1]

        current_detection = ""

        for r in results:
            for box in r.boxes:

                cls = int(box.cls[0])
                label = model.names[cls]

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                x_center = (x1 + x2) // 2
                position = get_position(x_center, frame_width)

                current_detection = f"{label} {position}"

                # ---------------- SPEECH CONTROL ----------------

                current_time = time.time()

                if (
                    current_detection != last_spoken_message and
                    current_time - last_spoken_time > SPEECH_DELAY
                ):
                    latest_message = current_detection
                    last_spoken_message = current_detection
                    last_spoken_time = current_time

                # ---------------- DRAW BOX ----------------------

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.putText(
                    frame,
                    current_detection,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

# ---------------- ROUTES -------------------

@app.route("/video")
def video():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# Frontend polling endpoint
@app.route("/detect")
def detect():
    return jsonify({"message": latest_message})

# Serve React Build
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# ---------------- RUN ----------------------

if __name__ == "__main__":
    print("✅ Vision Assist running at:")
    print("👉 http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)
