from flask import Flask, jsonify , request
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_marshmallow import Marshmallow
from sqlalchemy import func
from ultralytics import YOLO
from PIL import Image
import cv2 
import os
import time


app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root@127.0.0.1/flask"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app)
#ma = Marshmallow(app)
model = YOLO("yolov8n.pt")

class_names = []
with open("classes.txt", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

def delete_image(filename):
    try:
        os.remove(filename)  
        return True  
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False  

#@app.route('/' , methods = ['GET'])

@app.route('/camera' , methods = ['POST' , 'GET'])
def camera():
        if 'image' in request.files:
            image = request.files['image']
            img = Image.open(image)
            #img.save('image.png')
            results = model.predict(source = img)
            boxes = results[0].boxes.xyxy.tolist()
            classes = results[0].boxes.cls.tolist()
            if not classes:  
                return 'no class detected'
            response_data_list = []
            for box, cls in zip(boxes, classes):
                x1, y1, x2, y2 = box
                x1 = x1 // 18.5
                y1 = y1 // 9
                width = (x2 - x1) // 18.5
                height = (y2 - y1) // 9
                name = class_names[int(cls)]
                response_data = {
                    'x': x1,
                    'y': y1,
                    'width': width,
                    'height': height,
                    'class': name
                }

                response_data_list.append(response_data)
            print(response_data_list)
            return jsonify(response_data_list)
        return 'error'


if __name__ == "__main__":
    with app.app_context():
        #app.run(debug=True)
        #app.run(host = '192.168.1.14' , port=8081 , debug=True)
        app.run(host = '172.20.10.2' , port=8081 , debug=True)
