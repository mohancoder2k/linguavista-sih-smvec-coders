import speech_recognition as sr
import io
class SpeechToText:
    def __init__(self, mysql):
        self.mysql = mysql

    def extract_text_from_audio(self, audio_id, audio_data):
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(io.BytesIO(audio_data))

        with audio_file as source:
            audio_content = recognizer.record(source)

        try:
            # Using Google Web Speech API
            extracted_text = recognizer.recognize_google(audio_content)
            self.save_extracted_text(audio_id, extracted_text)
            return extracted_text
        except sr.UnknownValueError:
            raise ValueError("Could not understand audio.")
        except sr.RequestError as e:
            raise ValueError(f"Could not request results from Google Speech Recognition service; {e}")

    def save_extracted_text(self, audio_id, text):
        cursor = self.mysql.connection.cursor()
        query = "INSERT INTO stt (audio_id, text) VALUES (%s, %s)"
        cursor.execute(query, (audio_id, text))
        self.mysql.connection.commit()
        cursor.close()
