import speech_recognition as sr
recognizer = sr.Recognizer()
wav_file_path = "C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/voice-test.wav"

# Load the WAV file
with sr.AudioFile(wav_file_path) as source:
    audio_data = recognizer.record(source)

# Use the recognizer to transcribe speech from the WAV file
transcript = recognizer.recognize_google(audio_data)
print("Transcription:", transcript)
