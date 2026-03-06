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

object_model = YOLO("yolov8n.pt")
currency_model = YOLO("best.pt")

# ---------------- CAMERA -------------------

cap = cv2.VideoCapture(0)

latest_object_message = ""
latest_currency_message = ""

last_object_spoken = ""
last_object_time = 0

last_currency_spoken = ""
last_currency_time = 0

OBJECT_SPEECH_DELAY = 3
CURRENCY_SPEECH_DELAY = 6

# ---------------- POSITION LOGIC -----------

def get_position(x_center, frame_width):
    if x_center < frame_width / 3:
        return "on your left"
    elif x_center > 2 * frame_width / 3:
        return "on your right"
    else:
        return "ahead"

# ---------------- VIDEO STREAM -------------

def generate_frames(model):

    global latest_object_message, latest_currency_message
    global last_object_spoken, last_object_time
    global last_currency_spoken, last_currency_time

    while True:

        success, frame = cap.read()

        if not success:
            break

        results = model.predict(frame, stream=True)
        frame_width = frame.shape[1]

        detected = False

        for r in results:
            for box in r.boxes:

                detected = True

                cls = int(box.cls[0])
                label = model.names[cls]

                # Format currency speech
                if model == currency_model:
                    label = label.replace("_", " ")
                    label = label.replace("Rupee", " rupees")
                    label = label.replace(" coin", "")
                    label = label.replace(" note", "")

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                x_center = (x1 + x2) // 2
                position = get_position(x_center, frame_width)

                if model == currency_model:
                    current_detection = label
                else:
                    current_detection = f"{label} {position}"

                current_time = time.time()

                # OBJECT SPEECH
                if model == object_model:

                    if (
                        current_detection != last_object_spoken and
                        current_time - last_object_time > OBJECT_SPEECH_DELAY
                    ):
                        latest_object_message = current_detection
                        last_object_spoken = current_detection
                        last_object_time = current_time

                #CURRENCY SPEECH
                else:
                    if (
                        current_detection != last_currency_spoken and
                        current_time - last_currency_time > CURRENCY_SPEECH_DELAY
                    ):
                        latest_currency_message = current_detection
                        last_currency_spoken = current_detection

                    else:
                        latest_currency_message = current_detection
                    

                # DRAW BOX
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

        # -------- FIX FOR REPEATING AUDIO --------

        if not detected:
            if model == object_model:
                latest_object_message = ""
            else:
                latest_currency_message = ""

        # -----------------------------------------

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

# ---------------- ROUTES -------------------
@app.route("/video/object")
def video_object():
    return Response(
        generate_frames(object_model),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/video/currency")
def video_currency():
    return Response(
        generate_frames(currency_model),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# ---------------- DETECT API ----------------

@app.route("/detect/<mode>")
def detect(mode):

    if mode == "object":
        return jsonify({"message": latest_object_message})

    if mode == "currency":
        return jsonify({"message": latest_currency_message})

    return jsonify({"message": ""})

# ---------------- FRONTEND ----------------

@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# ---------------- RUN ----------------------

if __name__ == "__main__":
    print("✅ Vision Assist running at:")
    print("👉 http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)
