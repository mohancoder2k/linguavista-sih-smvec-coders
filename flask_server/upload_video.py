# upload_video.py
from flask_mysqldb import MySQL

class UploadVideo:
    def __init__(self, mysql):
        self.mysql = mysql
    
    def save_video(self, video_file):
        cursor = self.mysql.connection.cursor()
        
        # Read the video file as binary data
        video_data = video_file.read()
        
        # Insert the video data into the video_original table
        query = "INSERT INTO video_original (video_data) VALUES (%s)"
        cursor.execute(query, (video_data,))
        self.mysql.connection.commit()
        
        # Get the ID of the newly inserted video
        video_id = cursor.lastrowid
        
        # Close the cursor
        cursor.close()
        
        return video_id
