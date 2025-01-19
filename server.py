from flask import Flask, request, send_from_directory
import os
from dotenv import load_dotenv
import fal_client
import base64

load_dotenv()

app = Flask(__name__)

# Wizper PLAN

# - User uploads, make it statically available
# - Generate URL to send to fal
# - Share URL with fal for transcription
# - Delete from file system


@app.route("/")
def index():
    return """
    <h1>Upload File</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    """


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded"

    file = request.files["file"]

    # Check if the file is an audio file
    allowed_extensions = ["mp3", "ogg", "wav", "m4a", "aac"]

    if not file.filename.split(".")[-1] in allowed_extensions:
        return "Invalid file type. Supported file types: mp3, ogg, wav, m4a, aac"

    # Save the file into /static/upload
    filename = file.filename
    file.save(os.path.join("static/uploads", filename))

    # Read file and convert to base64
    file_path = os.path.join("static/uploads", filename)
    with open(file_path, "rb") as audio_file:
        encoded_bytes = base64.b64encode(audio_file.read())
        encoded_string = encoded_bytes.decode("utf-8")
        file_base64 = (
            f"data:audio/{file.filename.split('.')[-1]};base64,{encoded_string}"
        )

    def on_queue_update(update):
        if update and hasattr(update, "logs") and update.logs:
            for log in update.logs:
                print(log["message"])

    # Send to fal_ai API
    result = fal_client.subscribe(
        "fal-ai/wizper",
        arguments={"audio_url": file_base64},
        on_queue_update=on_queue_update,
    )

    print(result)

    return f"File uploaded successfully. Access it at: /static/uploads/{filename}"


@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory("static/uploads", filename)


if __name__ == "__main__":
    app.run(debug=True, port=3000)
