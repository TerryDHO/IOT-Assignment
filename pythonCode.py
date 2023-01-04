import cv2
import grovepi
import time
import datetime
from pyrebase import pyrebase
import base64


#Initialize Firebase
firebaseConfig = {
    "apiKey": "AIzaSyA-yTzWRKUlCCJCqhCnLcACJq6bRPsZvj4",
    "authDomain": "bait2123-iot-assignment-c2c1b.firebaseapp.com",
    "databaseURL": "https://bait2123-iot-assignment-c2c1b-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "bait2123-iot-assignment-c2c1b",
    "storageBucket": "bait2123-iot-assignment-c2c1b.appspot.com",
    "messagingSenderId": "1064848591736",
    "appId": "1:1064848591736:web:a0cf34ddbc1110e3a3d68d",
    "measurementId": "G-CSX4702KKX"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
user = auth.sign_in_with_email_and_password("rsdg1assignment@gmail.com", "RSDg1*assignment")
db = firebase.database()

# Connect the PIR sensor to digital port D4
pir_sensor = 4
grovepi.pinMode(pir_sensor,"INPUT")

# Set the camera rotation (optional)
camera_rotation = 180

# Initialize the webcam
camera = cv2.VideoCapture(0)

pir_count = 0

while True:
    # Read the sensor state
    pir_state = db.child("pir_sensor_state").get().val()
    
    if pir_state == '1':
        pir_threshold = 100
        
        
        motion_sensor_status = grovepi.digitalRead(pir_sensor)
        
        if motion_sensor_status == 1:
            if pir_threshold > 0:
                pir_count += 1
                if pir_count > pir_threshold:
                   
                    print("Motion has been detected in your area")
                    #Get reference from the database
                    images_ref = db.child("images")
                    #Read the webcam frame
                    
                    ret, frame = camera.read()
                    #Save the image as a JPEG file on the raspberry pi
                    image_filename = "image.jpg"
                    
                    cv2.imwrite(image_filename, frame)
                    #Open the image file and read the image data 
                    with open(image_filename, "rb") as image_file:
                        image_data = image_file.read()
                    
                    #Encode the image data as a base64 string
                    image_data = base64.b64encode(image_data)
                    
                    #Get the current date and time and format the date and
                    #time as a string
                    now = datetime.datetime.now()
                    date_time = now.strftime("%Y-%m-%d_%I-%M-%S_%p")
                
                    #Get the reference to the "images" child in the database
                    image_ref = db.child("images")
                    
                
                    #Get a reference to a new child with the unique ID
                    #(current date and time)
                    image_ref = images_ref.child(date_time)
                    
                    # Save the image to the Firebase Realtime Database
                    image_ref.set({
                        "image_data": image_data.decode("utf-8")
                    })
                    
                    #Save the image to the "recent_image" datafield
                    recent_image_ref = db.child("recent_image")
                    recent_image_ref.set({
                        "image_data": image_data.decode("utf-8")
                    })
                    
                    #When motion is detected
                    notification_sensor_ref = db.child("notification_sensor")
                    notification_sensor_ref.set(1)
                    #Reset the count to 0
                    pir_count = 0
                        
    else:
        pir_threshold = 1
        notification_sensor_ref = db.child("notification_sensor")
        notification_sensor_ref.set(0)        
           
# Release the webcam
camera.release()
# Close all windows
cv2.destroyAllWindows()
