import speech_recognition as sr
from moviepy.editor import *

recognizer = sr.Recognizer()

def convert_mp4_to_wav(mp4_file, wav_file):
    video_clip = VideoFileClip(mp4_file)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(wav_file)
    
source_path = 'C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/videos/video.mp4'
wav_path = "C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/videos/output.wav"

convert_mp4_to_wav(source_path, wav_path)
    

# Load the WAV file
with sr.AudioFile(wav_path) as source:
    audio_data = recognizer.record(source)

# Use the recognizer to transcribe speech from the WAV file
transcript = recognizer.recognize_google(audio_data)
print("Transcription:", transcript)
