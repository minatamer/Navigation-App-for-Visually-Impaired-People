from gtts import gTTS
import os

# Arabic text to be converted to speech

def translate_to_arabic(word):
    translations = {
        "bed": "سرير",
        "chair": "كرسي",
        "couch": "أريكة",
        "door_closed": "باب مغلق",
        "door_open": "باب مفتوح",
        "obstacle": "عائق",
        "oven": "فرن",
        "person": "شخص",
        "refrigerator": "ثلاجة",
        "sink": "حوض",
        "stairs": "سلالم",
        "table": "طاولة",
        "television": "تلفزيون",
        "toilet": "الحمام"
    }
    
    return translations.get(word, "Translation not available")

# object = "الهاتف المحمول"
object = translate_to_arabic('toilet')
distance = "200"
arabic_text = object + "على بعد" + distance+ "سنتيمتر" 


# Create a gTTS object
tts = gTTS(text=arabic_text, lang='ar')

# Save the audio to a file
tts.save("C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/AppProject/assets/output.mp3")

# Play the audio file
# os.system("start output.mp3")
