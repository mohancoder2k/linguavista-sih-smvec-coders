import speech_recognition as sr
from pydub import AudioSegment

def audio_to_text(audio_file):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load audio file
    audio = AudioSegment.from_file(audio_file)

    # Export audio to WAV format for better compatibility
    wav_file = "temp.wav"
    audio.export(wav_file, format="wav")

    # Split the audio into chunks (e.g., 30 seconds each)
    chunk_length_ms = 30000  # 30 seconds
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]

    full_transcription = ""

    for i, chunk in enumerate(chunks):
        # Export each chunk to a temporary WAV file
        chunk_wav_file = f"temp_chunk_{i}.wav"
        chunk.export(chunk_wav_file, format="wav")

        # Use the chunk as the audio source
        with sr.AudioFile(chunk_wav_file) as source:
            audio_data = recognizer.record(source)  # Read the entire chunk

        # Recognize the speech using Google Web Speech API
        try:
            print(f"Recognizing chunk {i + 1} of {len(chunks)}...")
            text = recognizer.recognize_google(audio_data)
            print("Extracted text: " + text)
            full_transcription += text + " "  # Append the text to the full transcription
        except sr.UnknownValueError:
            print(f"Sorry, could not understand chunk {i + 1}.")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")

    print("Full Transcription:")
    print(full_transcription)

if __name__ == "__main__":
    audio_file_path = r"C:\Users\Dell\Downloads\audio.mp3"  # Replace with your audio file path
    audio_to_text(audio_file_path)
