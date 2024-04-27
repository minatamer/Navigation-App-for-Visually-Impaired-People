from flask import Flask, jsonify , request
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import cv2 as cv
import os
from gtts import gTTS
import math
import time
import datetime

# Distance constants 
KNOWN_DISTANCE = 45 #INCHES
PERSON_WIDTH = 16 #INCHES #525.5 pixels
MOBILE_WIDTH = 3.0 #INCHES 
CHAIR_WIDTH = 24.0 #INCHES #307 pixels
# BOTTLE_WIDTH = 2.0 #INCHES #44.8 pixels
TABLE_WIDTH = 42.0 #INCHES #942.2 pixels
DOOR_CLOSED_WIDTH = 31.5 #INCHES #706.5 pixels
DOOR_OPENED_WIDTH = 35.4 #INCHES #794 pixels
FRIDGE_WIDTH= 27.5 #INCHES #616.9 pixels
OBSTACLE_WIDTH= 10 #INCHES #224.3 pixels
COUCH_WIDTH= 82.6  #INCHES #1852 pixels
OVEN_WIDTH= 31.5 #INCHES #706.7 pixels
SINK_WIDTH= 23.6 #INCHES #529.4 pixels
TV_WIDTH=  39.3 #INCHES #881.6 pixels
TOILET_WIDTH= 13.8 #INCHES #309.6 pixels
BED_WIDTH= 47.2 #INCHES #1058 pixels
STAIRS_WIDTH= 42 #INCHES #941 pixels


# colors for object detected
COLORS = [(255,0,0),(255,0,255),(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]
GREEN =(0,255,0)
BLACK =(0,0,0)
# defining fonts 
FONTS = cv.FONT_HERSHEY_COMPLEX

app = Flask(__name__)
# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
model = YOLO("best.pt")

class_names = []
with open("classes_new.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

speech_counter = 6

def increment_counter():
    global speech_counter
    speech_counter = speech_counter + 1

# focal length finder function 
def focal_length_finder (measured_distance, real_width, width_in_rf):
    focal_length = (width_in_rf * measured_distance) / real_width

    return focal_length

# distance finder function 
def distance_finder(focal_length, real_object_width, width_in_frmae):
    distance = (real_object_width * focal_length) / width_in_frmae
    return distance

def object_detector(image):
    results = model.predict(source = image , verbose=False)
    boxes = results[0].boxes.xyxy.tolist()
    classes = results[0].boxes.cls.tolist()
    names = results[0].names
    confidences = results[0].boxes.conf.tolist()
    # creating empty list to add objects data
    data_list =[]
    for box, cls, conf in zip(boxes, classes, confidences):
        x1, y1, x2, y2 = box
        confidence = conf
        detected_class = cls
        width = x2-x1
        height = y2-y1
        # getting the data 
        # if int(detected_class) ==0 or int(detected_class) ==67 or int(detected_class) == 56 or int(detected_class) == 39 or int(detected_class) == 60: 
        if (int(detected_class) >= 0 and int(detected_class) <=13):
            data_list.append(class_names[int(detected_class)])
            data_list.append(x1)             
            data_list.append(y1)
            data_list.append(width)
            data_list.append(height)
        # returning list containing the object data. 
    return data_list


def delete_image(filename):
    try:
        os.remove(filename)  
        return True  
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False  
    
# person_data = object_detector('ReferenceImagesV8/person.png')
person_data = 525.5
focal_person = focal_length_finder(KNOWN_DISTANCE, PERSON_WIDTH, person_data)

# chair_data = object_detector('ReferenceImagesV8/chair.png')
chair_data = 307
focal_chair = focal_length_finder(KNOWN_DISTANCE, CHAIR_WIDTH, chair_data)

table_data = 942.2
focal_table = focal_length_finder(KNOWN_DISTANCE, TABLE_WIDTH, table_data)

door_closed_data = 706.5
focal_door_closed = focal_length_finder(KNOWN_DISTANCE, DOOR_CLOSED_WIDTH, door_closed_data)

door_opened_data = 794
focal_door_opened = focal_length_finder(KNOWN_DISTANCE, DOOR_OPENED_WIDTH, door_opened_data)

# mobile_data = object_detector('ReferenceImagesV8/cellphone.png')
# focal_mobile = focal_length_finder(KNOWN_DISTANCE, MOBILE_WIDTH, mobile_data[1])

fridge_data = 616.9
focal_fridge = focal_length_finder(KNOWN_DISTANCE, FRIDGE_WIDTH, fridge_data)

obstacle_data = 224.3
focal_obstacle = focal_length_finder(KNOWN_DISTANCE, OBSTACLE_WIDTH, obstacle_data)

couch_data = 224.3
focal_couch = focal_length_finder(KNOWN_DISTANCE, COUCH_WIDTH, couch_data)

oven_data = 224.3
focal_oven = focal_length_finder(KNOWN_DISTANCE, OVEN_WIDTH, oven_data)

sink_data = 224.3
focal_sink = focal_length_finder(KNOWN_DISTANCE, SINK_WIDTH, sink_data)

tv_data = 224.3
focal_tv = focal_length_finder(KNOWN_DISTANCE, TV_WIDTH, tv_data)

toilet_data = 224.3
focal_toilet = focal_length_finder(KNOWN_DISTANCE, TOILET_WIDTH, toilet_data)

bed_data = 1058
focal_bed = focal_length_finder(KNOWN_DISTANCE, BED_WIDTH, bed_data)

stairs_data = 941
focal_stairs = focal_length_finder(KNOWN_DISTANCE, STAIRS_WIDTH, stairs_data)


#@app.route('/' , methods = ['GET'])

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


@app.route('/camera' , methods = ['POST' , 'GET'])
def camera():
        if 'image' in request.files:
            image = request.files['image']
            img = Image.open(image)
            data = object_detector(img) 
            response_data_list = []
            for i in range(0 , len(data) , 5):
                # if data[i + 0] =='cell phone' or data[i + 0] =='person' or data[i + 0] == 'chair' :
                #     if data[i + 0] =='cell phone' :
                #         distance = distance_finder (focal_mobile, MOBILE_WIDTH, data[i + 1])
                #     elif data[i + 0] =='person' :  
                #         distance = distance_finder (focal_person, PERSON_WIDTH, data[i + 1]) 
                #     elif data[i + 0] =='chair' :   
                #         distance = distance_finder (focal_chair, CHAIR_WIDTH, data[i + 1]) 
                if data[i + 0] =='person' or data[i + 0] == 'chair' or data[i + 0] == 'table' or data[i + 0] == 'door_closed' or data[i + 0] == 'door_open' or data[i + 0] == 'refrigerator' or data[i + 0] == 'obstacle' or data[i + 0] == 'couch' or data[i + 0] == 'oven'  or data[i + 0] == 'sink' or data[i + 0] == 'television' or data[i + 0] == 'toilet' or data[i + 0] == 'bed' or data[i + 0] == 'stairs' :
                    if data[i + 0] =='person' :   
                        distance = distance_finder (focal_person, PERSON_WIDTH, data[i + 3]) 
                    elif data[i + 0] =='chair' :   
                        distance = distance_finder (focal_chair, CHAIR_WIDTH, data[i + 3]) 
                    elif data[i + 0] =='table' :   
                        distance = distance_finder (focal_table, TABLE_WIDTH, data[i + 3]) 
                    elif data[i + 0] =='door_closed' :   
                        distance = distance_finder (focal_door_closed, DOOR_CLOSED_WIDTH, data[i + 3]) 
                    elif data[i + 0] =='door_open' :   
                        distance = distance_finder (focal_door_opened, DOOR_OPENED_WIDTH, data[i + 3])
                    elif data[i + 0] =='refrigerator' :   
                        distance = distance_finder (focal_fridge, FRIDGE_WIDTH, data[i + 3])
                    elif data[i + 0] =='obstacle' :   
                        distance = distance_finder (focal_obstacle, OBSTACLE_WIDTH, data[i + 3])
                    elif data[i + 0] =='couch' :   
                        distance = distance_finder (focal_couch, COUCH_WIDTH, data[i + 3])
                    elif data[i + 0] =='oven' :   
                        distance = distance_finder (focal_oven, OVEN_WIDTH, data[i + 3])
                    elif data[i + 0] =='sink' :   
                        distance = distance_finder (focal_sink, SINK_WIDTH, data[i + 3])
                    elif data[i + 0] =='television' :   
                        distance = distance_finder (focal_tv, TV_WIDTH, data[i + 3])
                    elif data[i + 0] =='toilet' :   
                        distance = distance_finder (focal_toilet, TOILET_WIDTH, data[i + 3])
                    elif data[i + 0] =='bed' :   
                        distance = distance_finder (focal_bed, BED_WIDTH, data[i + 3])
                    elif data[i + 0] =='stairs' :   
                        distance = distance_finder (focal_stairs, STAIRS_WIDTH, data[i + 3])
                x = data[i + 1] // 18.5
                y = data[i + 2] // 9
                width = data[i + 3] // 9.25
                height = data[i + 4] // 9
                distance = distance * 2.54 #conversion to cm
                response_data = {
                    'class': data[i + 0],
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'distance': distance
                } 
                # ARABIC TRANSLATION PART
                print("Current counter" , speech_counter)
                if data[i + 0] is not None and data[i + 0] != "" and distance<=50 and speech_counter % 6 == 0:
                    object_ar = translate_to_arabic(data[i + 0])
                    distance_rounded = math.ceil(distance)
                    arabic_text = object_ar + "على بعد" + str(distance_rounded)+ "سنتيمتر"
                    tts = gTTS(text=arabic_text, lang='ar') 
                    tts.save("C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/AppProject/output.mp3")
                    response_data['arabic'] = 'yes'
                    increment_counter()
                if (speech_counter % 6 != 0 ):
                    increment_counter()
                response_data_list.append(response_data)
            print(response_data_list)
            return jsonify(response_data_list)
        return 'error'

@app.route('/video', methods=['POST' , 'GET'])
def save_video():
    if 'video' not in request.files:
        return 'No file part', 400

    file = request.files['video']
    # Replace '/path/to/save/video/' with the path where you want to save the video file
    save_directory = os.path.join(app.root_path, 'videos')  # Save videos in 'videos' directory within Flask project
    os.makedirs(save_directory, exist_ok=True)  # Create directory if it doesn't exist
    file.save(os.path.join(save_directory, 'video.mp4'))  # Save file to specified directory
    # file.save('C:/Users/Mina/Desktop/bachelor/Navigation-App-for-Visually-Impaired-People/AppProject/video.mp4')

    return 'Video saved successfully', 200

if __name__ == "__main__":
    with app.app_context():
        # app.run(debug=True)
        #app.run(host = '192.168.1.14' , port=8081 , debug=True)
        app.run(host = '192.168.1.15' , port=8080 , debug=True)
        # app.run(host = '172.20.10.2' , port=8081 , debug=True)
        # app.run(host = '172.20.10.4' , port=8081 , debug=True)
