# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import cv2

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

pin=[4,17,27,22,18] # pump output pins
soil=[24,25,5,6,13,26] # soil moisture sensor input pins
thres=[1000000,1000000,1000000,1000000,1000000] # camera threshold (depends on the lighting condition)

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
for i in soil:
    GPIO.setup(i, GPIO.IN)
for i in pin:
    GPIO.setup(i, GPIO.OUT)
# allow the camera to warmup
time.sleep(0.1)
i=0

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    y,x,z=image.shape
    n=5
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    green_sum=[0]*n
    for p in range(1,n+1):
        for i in image:
            for j in range((p-1)*x//n,p*x//n):
                green_sum[p-1]+=i[j][1]
    
    for i in range(n):
        if(green_sum[i]>thres[i] and GPIO.input(soil[i])==1):
            GPIO.output(pin[i], GPIO.LOW) # turn off the pump
        else:
            GPIO.output(pin[i], GPIO.HIGH) # turn on the pump
    
    # show the frame
    for i in range(1,n):
        start_point=(i*x//n,0)
        end_point=(i*x//n,y)
        cv2.line(image, start_point, end_point, (255,255,255), 2)
    cv2.imshow("Frame", image)

    print(green_sum)
    
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        cv2.destroyAllWindows()
        print("closed")
        break
