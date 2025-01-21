from flask import Flask, request, send_from_directory, render_template, make_response
import os
from dotenv import load_dotenv
import fal_client
import random
import time

load_dotenv()

FLY_URL = os.getenv("FLY_URL")

app = Flask(__name__)


def format_timestamp(number):
    return f"{float(number):.2f}"


def process_transcription_result(raw_result):
    text = raw_result.get("text", "")
    chunks = raw_result.get("chunks", [])

    # Format chunks with consistent timestamp precision
    formatted_chunks = []
    for chunk in chunks:
        formatted_chunk = {
            "timestamp": [
                format_timestamp(chunk["timestamp"][0]),
                format_timestamp(chunk["timestamp"][1]),
            ],
            "text": chunk["text"],
        }
        formatted_chunks.append(formatted_chunk)

    return {"text": text, "chunks": formatted_chunks}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    file_extension = file.filename.split(".")[-1]

    # Save the file into /static/upload with a unique filename
    unique_filename = f"{int(time.time())}_{random.randint(1000,9999)}.{file_extension}"
    file.save(os.path.join("static/uploads", unique_filename))

    # Generate the URL to send to fal
    file_url = f"https://{FLY_URL}/static/uploads/{unique_filename}"

    # test_file = "https://github.com/mikeesto/wizzzper/raw/refs/heads/master/static/uploads/test.mp3"

    def on_queue_update(update):
        if update and hasattr(update, "logs") and update.logs:
            for log in update.logs:
                print(log["message"])

    # Send to fal_ai API
    response = fal_client.subscribe(
        "fal-ai/wizper",
        arguments={
            "audio_url": file_url,
        },
        on_queue_update=on_queue_update,
    )

    # Sample response
    # sample_result = {
    #     "text": "I have the pleasure to present to you Dr. Martin Luther King, Jr. I am happy to join with you today in what will go down in history as the greatest demonstration for freedom in the history of our nation.",
    #     "chunks": [
    #         {
    #             "timestamp": [0.2, 29.04],
    #             "text": "I have the pleasure to present to you Dr. Martin Luther King, Jr. I am happy to join with you today in what will go down in history as the greatest demonstration for freedom in the history of our nation.",
    #         }
    #     ],
    # }

    # Format the timestamps before sending to template
    result = process_transcription_result(response)
    return render_template("result.html", result=result)


@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory("static/uploads", filename)


@app.route("/download", methods=["POST"])
def download():
    data = request.json["transcript"]

    formatted_chunks = [
        f"{chunk['timestamp'][0]} - {chunk['timestamp'][1]}\n{chunk['text']}"
        for chunk in data
    ]
    formatted_transcript = "\n\n".join(formatted_chunks)

    response = make_response(formatted_transcript)
    response.headers["Content-Disposition"] = "attachment; filename=transcript.txt"
    response.headers["Content-Type"] = "text/plain"

    return response


if __name__ == "__main__":
    app.run(debug=True, port=3000)
