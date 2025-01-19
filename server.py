from flask import Flask, request, send_from_directory, render_template, make_response
import os
from dotenv import load_dotenv
import fal_client
import random
import time

load_dotenv()

app = Flask(__name__)

# Wizper PLAN

# - User uploads, make it statically available
# - Generate URL to send to fal
# - Share URL with fal for transcription
# - Delete from file system


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]

    # Check if the file is an audio file
    allowed_extensions = ["mp3", "ogg", "wav", "m4a", "aac"]

    file_extension = file.filename.split(".")[-1]

    if not file.filename.split(".")[-1] in allowed_extensions:
        return "Invalid file type. Supported file types: mp3, ogg, wav, m4a, aac"

    # Save the file into /static/upload with a unique filename
    unique_filename = f"{int(time.time())}_{random.randint(1000,9999)}.{file_extension}"
    file.save(os.path.join("static/uploads", unique_filename))

    test_file = "https://github.com/mikeesto/wizzzper/raw/refs/heads/master/static/uploads/test.mp3"

    def on_queue_update(update):
        if update and hasattr(update, "logs") and update.logs:
            for log in update.logs:
                print(log["message"])

    # Send to fal_ai API
    # result = fal_client.subscribe(
    #     "fal-ai/wizper",
    #     arguments={
    #         "audio_url": test_file,
    #     },
    #     on_queue_update=on_queue_update,
    # )

    # print(result)

    # Sample response
    result = {
        "text": "I have the pleasure to present to you Dr. Martin Luther King, Jr. I am happy to join with you today in what will go down in history as the greatest demonstration for freedom in the history of our nation.",
        "chunks": [
            {
                "timestamp": [0.2, 29.04],
                "text": "I have the pleasure to present to you Dr. Martin Luther King, Jr. I am happy to join with you today in what will go down in history as the greatest demonstration for freedom in the history of our nation.",
            }
        ],
    }

    return render_template("result.html", result=result)


@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory("static/uploads", filename)


@app.route("/download", methods=["POST"])
def download():
    data = request.json

    formatted_transcript = data.map(
        lambda chunk: f"{chunk["timestamp"]}\n{chunk["text"]}"
    ).join("\n\n")

    response = make_response(formatted_transcript)
    response.headers["Content-Disposition"] = "attachment; filename=transcript.txt"
    response.headers["Content-Type"] = "text/plain"

    return response


if __name__ == "__main__":
    app.run(debug=True, port=3000)
