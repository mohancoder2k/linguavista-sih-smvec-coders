# extract_audio.py
from flask_mysqldb import MySQL
import moviepy.editor as mp
import os

class ExtractAudio:
    def __init__(self, mysql):
        self.mysql = mysql

    def extract_audio_from_video(self, video_id):
        cursor = self.mysql.connection.cursor()
        
        # Fetch the video data from the database
        query = "SELECT video_data FROM video_original WHERE id = %s"
        cursor.execute(query, (video_id,))
        video_record = cursor.fetchone()

        if not video_record:
            cursor.close()
            raise ValueError("Video not found with the given ID.")

        video_data = video_record['video_data']

        # Save the video data to a temporary file
        video_path = f"temp_video_{video_id}.mp4"
        with open(video_path, 'wb') as video_file:
            video_file.write(video_data)

        # Extract audio using moviepy
        audio_path = f"extracted_audio_{video_id}.mp3"
        video_clip = mp.VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
        
        # Read the audio file as binary data
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Insert the audio data into the audio_extracted table
        self.save_audio(audio_data)

        # Clean up temporary files
        audio_clip.close()
        video_clip.close()
        os.remove(video_path)
        os.remove(audio_path)

        cursor.close()

    def save_audio(self, audio_data):
        cursor = self.mysql.connection.cursor()
        
        # Insert the audio data into the audio_extracted table
        query = "INSERT INTO audio_extracted (audio_data) VALUES (%s)"
        cursor.execute(query, (audio_data,))
        self.mysql.connection.commit()
        
        # Close the cursor
        cursor.close()
