from flask import Flask, request, jsonify, send_file
from flask_mysqldb import MySQL
from upload_video import UploadVideo
from extract_audio import ExtractAudio
from speech_to_text import SpeechToText  # Import the SpeechToText class
import io

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'linguavista'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL
mysql = MySQL(app)

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file part"}), 400
    
    video_file = request.files['video']
    
    if video_file.filename == '':
        return jsonify({"error": "No selected video file"}), 400
    
    if video_file:
        uploader = UploadVideo(mysql)
        video_id = uploader.save_video(video_file)
        return jsonify({"message": "Video uploaded successfully", "video_id": video_id}), 201

@app.route('/extract_audio', methods=['POST'])
def extract_audio():
    if 'video_id' not in request.json:
        return jsonify({"error": "No video ID provided"}), 400
    
    video_id = request.json['video_id']
    
    extractor = ExtractAudio(mysql)
    
    try:
        extractor.extract_audio_from_video(video_id)
        return jsonify({"message": "Audio extracted and saved successfully"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/get_audio/<int:audio_id>', methods=['GET'])
def get_audio(audio_id):
    cursor = mysql.connection.cursor()
    
    # Fetch the audio data from the database
    query = "SELECT audio_data FROM audio_extracted WHERE id = %s"
    cursor.execute(query, (audio_id,))
    audio_record = cursor.fetchone()
    
    cursor.close()

    if audio_record:
        audio_data = audio_record['audio_data']
        return send_file(io.BytesIO(audio_data), mimetype='audio/mpeg', as_attachment=True, download_name=f"extracted_audio_{audio_id}.mp3")
    else:
        return jsonify({"error": "Audio not found with the given ID."}), 404
    
@app.route('/extract_text', methods=['POST'])
def extract_text():
    if 'audio_id' not in request.json:
        return jsonify({"error": "No audio ID provided"}), 400
    
    audio_id = request.json['audio_id']
    
    # Fetch the audio data from the database
    cursor = mysql.connection.cursor()
    query = "SELECT audio_data FROM audio_extracted WHERE id = %s"
    cursor.execute(query, (audio_id,))
    audio_record = cursor.fetchone()
    cursor.close()

    if audio_record:
        audio_data = audio_record['audio_data']
        print(f"Audio data retrieved: {len(audio_data)} bytes")  # Debugging line
        
        # Extract text from audio
        stt_processor = SpeechToText(mysql)
        try:
            extracted_text = stt_processor.extract_text_from_audio(audio_id, audio_data)
            return jsonify({"message": "Text extracted successfully", "extracted_text": extracted_text}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "Audio not found with the given ID."}), 404

if __name__ == '__main__':
    app.run(debug=True)
