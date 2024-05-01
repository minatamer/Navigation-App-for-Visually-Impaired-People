import whisper

model = whisper.load_model("base")
source_path = 'C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/videos/video.mp4'
result = model.transcribe(source_path , language='Arabic', fp16=False)
transcribed_text = result["text"]
# contains_change = "تغير" in transcribed_text
# contains_change2 = "تغيير" in transcribed_text
# contains_change3 = "لغة" in transcribed_text
# contains_change4 = "اللغة" in transcribed_text
contains_no = "لا" in transcribed_text
print(contains_no)