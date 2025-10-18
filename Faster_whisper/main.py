import os
from flask import Flask, request
from faster_whisper import WhisperModel
from google.cloud import storage

app = Flask(__name__)

# --- Configuration ---
MODEL_SIZE = "base"
TRANSCRIPT_BUCKET_NAME = os.environ.get("TRANSCRIPT_BUCKET_NAME") 

# --- Model Loading (CPU Version) ---
print(f"Loading faster-whisper model: {MODEL_SIZE} on CPU")
# Key Changes: device="cpu" and compute_type="int8"
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print("Model loaded successfully.")

@app.route('/', methods=['POST'])
def transcribe_audio():
    # --- 1. Parse the Eventarc message ---
    message = request.get_json()
    print(f"Received message: {message}")

    bucket_name = message['bucket']
    file_name = message['name']
    
    # --- 2. Download the audio file from Cloud Storage ---
    storage_client = storage.Client()
    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(file_name)
    
    temp_file_path = f"/tmp/{os.path.basename(file_name)}"
    source_blob.download_to_filename(temp_file_path)
    print(f"Downloaded {file_name} to {temp_file_path}")

    # --- 3. Transcribe using faster-whisper ---
    print("Starting transcription on CPU...")
    # This part of the code doesn't need to change
    segments, _ = model.transcribe(temp_file_path, beam_size=5)
    
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    print(f"Transcription complete: {transcript[:100]}...")

    # --- 4. Upload the transcript back to Cloud Storage ---
    if TRANSCRIPT_BUCKET_NAME:
        transcript_file_name = f"{os.path.splitext(os.path.basename(file_name))[0]}.txt"
        destination_bucket = storage_client.bucket(TRANSCRIPT_BUCKET_NAME)
        destination_blob = destination_bucket.blob(transcript_file_name)
        
        destination_blob.upload_from_string(transcript)
        print(f"Uploaded transcript to gs://{TRANSCRIPT_BUCKET_NAME}/{transcript_file_name}")

    # --- 5. Clean up ---
    os.remove(temp_file_path)
    
    return ("OK", 204)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))