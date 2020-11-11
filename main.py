import cv2
import threading
import notifacation
import util
import datetime
import json

showImages = True
settings = util.getSettings()
cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorKNN()
activeState = False
active = False
armed = False
recordingTime = 10.0
timer = None
startDelay = 5.0
startDelayTimer = None
notifacationThread = None
out = cv2.VideoWriter(settings["videoOut"] + "wackyerror.mp4",cv2.VideoWriter_fourcc('M','P','4','V'), 15.0, (640,480))

def onTimer():
    global active
    active = False
    print("Stop doing")
    #release writer

def setTimer():
    global timer
    timer = threading.Timer( recordingTime, onTimer)

def postDelay():
    global armed 
    armed = True
    print("Armed")


def setStartDelayTimer():
    global startDelayTimer
    startDelayTimer = threading.Timer( startDelay, postDelay)

def getMotion( frame):
    global backsub
    frame = cv2.GaussianBlur(frame, (41,41), cv2.BORDER_DEFAULT)
    frame = backSub.apply(frame)
    return frame

def percentWhite( frame, motionFrame):
    numWhite = motionFrame[motionFrame > 10].size
    totalPix = motionFrame.size
    percentWhite = round( 10000 * numWhite / totalPix) / 100    
    return percentWhite

def resetTimer():
    if not timer == None:
        if timer.is_alive():
            timer.cancel()
            #print("Timer reset")

def motionDetected():
    global active
    global timer
    
    # This only gets run initially on motion
    if not active and armed:
        print("Motion detected!")
        #alertGroup needs to be threaded so that it doesn't lag the program
        notifacationThread = threading.Thread( target = notifacation.alertGroup, args = ("Motion detected laptop", ))
        #notifacation.alertGroup("Motion detected test")
        notifacationThread.start()
        active = True
        resetTimer()
        setTimer()
        timer.start()
        out = cv2.VideoWriter(settings["videoOut"] + "RecordingName.mp4",cv2.VideoWriter_fourcc('M','P','4','V'), 15.0, (640,480))
        #start timer
        #notify user(make new func for multiple receivers)
        #initialize global VideoWriter variable
    else: 
        if active and armed:
            resetTimer()
            setTimer()
            timer.start()

def main():
    while 1:
        ret, frame = cap.read()
        motionFrame = getMotion( frame)
        motionDetectedBool = percentWhite( frame, motionFrame) > 4.0
        # Show images
    
        if motionDetectedBool:
            motionDetected()
            motionFrame = cv2.putText( motionFrame, "Motion Detected", (10,22), cv2.FONT_HERSHEY_SIMPLEX, .7, (100,100,100), 1)


        if showImages:
            cv2.imshow("Frame", frame)
            cv2.imshow("Motion", motionFrame)

        if active:
            #output to video file
            #out = cv2.VideoWriter(settings["videoOut"] + "RecordingName.mp4",cv2.VideoWriter_fourcc('M','P','G','4'), 15.0, (640,480))
            out.write(frame)
            #print("I should write here")

        #exit when user presses q
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            if not timer == None:
                if timer.is_alive():
                    timer.cancel()
            break     

# Initialize background photo so that it doesn't start automatically saying motion is detected
#ret, frame = cap.read()
#for i in range(5):
#    backSub.apply( frame)
setStartDelayTimer()
startDelayTimer.start()
main()
