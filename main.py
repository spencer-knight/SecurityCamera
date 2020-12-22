import threading
import datetime
import json
import time
import os
import numpy as np
import init
init.run()
import notifacation
import util
    
try:
    from flask import Flask, render_template, render_template_string, Response, redirect, url_for, request
except:
    util.install("flask")
    from flask import Flask, render_template, render_template_string, Response, redirect, url_for, request

try:
    from dateutil import tz
except:
    util.install("python-dateutil")
    from dateutil import tz

try:
    import psutil
except:    
    util.install("psutil")
    import psutil

try:
    import cv2
except:
    util.install("opencv-contrib-python")
    import cv2

settings = util.getSettings()
startDelay = settings["startDelay"]
recordingTime = settings["recordingTime"]
showImages = settings["showImages"]
timezone = tz.gettz(settings["timeZone"])

cap = cv2.VideoCapture(0)
backSub = cv2.createBackgroundSubtractorKNN()
activeState = False
active = False
armed = False
timer = None
startDelayTimer = None
notifacationThread = None
out = None 
frame = None
flaskThread = None
displayString = None
motionFrame = None
timeString = None
websiteOffset = settings["websiteOffset"]

# Run once the recording timer stops, this means it is the end of the recording period.
def onTimer():
    global active
    global out
    active = False
    print("Stop doing")
    #out.release() For some reason releaseing the object causes a segmentation fault.
    out = None

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
    #frame = cv2.fastNlMeansDenoisingColored(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.bilateralFilter(frame, 7, 50, 50)
    #frame = cv2.GaussianBlur(frame, (41,41), cv2.BORDER_DEFAULT)
    frame = cv2.Canny( frame, 60, 240)
    frame = cv2.GaussianBlur(frame, (41,41), cv2.BORDER_DEFAULT)
    frame = backSub.apply(frame)
    kernel = np.ones((60,60),np.uint8)
    frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)
    return frame

def percentWhite( motionFrame):
    numWhite = motionFrame[motionFrame > 10].size
    totalPix = motionFrame.size
    percentWhite = round( 10000 * numWhite / totalPix) / 100    
    return percentWhite

def resetTimer():
    if not timer == None:
        if timer.is_alive():
            timer.cancel()

def motionDetected():
    global active
    global timer
    global out
    
    # This only gets run initially on motion
    if not active and armed:
        print("Motion detected!")

        #alertGroup needs to be threaded so that it doesn't stop the camera
        notifacationThread = threading.Thread( target = notifacation.alertGroup, args = (settings["alertMessage"], ))
        notifacationThread.start()
        timeInfo = datetime.datetime.now()
        recName = timeInfo.strftime(settings["fileNameFormat"])
        out = cv2.VideoWriter(settings["videoOut"] + recName + ".webm",cv2.VideoWriter_fourcc(*"VP80"), settings["outfileFramerate"], (640,480))#
        active = True
        resetTimer()
        setTimer()
        timer.start()
        #might add check to see if file already exists, then add something so that stuff doesn't get overwritten
    else: 
        if active and armed:
            resetTimer()
            setTimer()
            timer.start()

def get_performance():
    return "cpu: " + str(psutil.cpu_percent()) + " ram: " + str(psutil.virtual_memory().percent)

def grabFrames():
    global frame

    print("Frame grabber thread started")

    while True:
        ret, lFrame = cap.read()
        if ret:
            frame = lFrame
        time.sleep(settings["loopDelay"])

def determineMotion():
    global frame
    global motionFrame

    print("Algorithm thread started")

    while True:
        motionFrame = getMotion( frame)
        motionDetectedBool = percentWhite( motionFrame) > 4.0
        
        if motionDetectedBool:
            motionDetected()
            motionFrame = cv2.putText( motionFrame, "Motion Detected", (10,22), cv2.FONT_HERSHEY_SIMPLEX, .7, (100,100,100), 1)
        time.sleep(settings["loopDelay"])
    

def main():
    global frame
    global motionFrame
    global displayString
    global active
    global timeString

    while 1:
        displayString = get_performance()
        if active:
            displayString += " active" 
        #ret, frame = cap.read()
        #frame = cv2.resize( frame, (640,480))
        #motionFrame = getMotion( frame)
        #motionDetectedBool = percentWhite( motionFrame) > 4.0
    
        #if motionDetectedBool:
        #    motionDetected()
        #    motionFrame = cv2.putText( motionFrame, "Motion Detected", (10,22), cv2.FONT_HERSHEY_SIMPLEX, .7, (100,100,100), 1)


        #timeInfo = datetime.datetime.now(tz=timezone)
        #timeString = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #recName = timeString
        outFrame = frame
        #timeSize = cv2.getTextSize(recName, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        #displaySize = cv2.getTextSize(displayString, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        #outFrame = cv2.rectangle( outFrame, (10,470 - timeSize[0][1]), (10 + timeSize[0][0], 470), (30,30,30), 10)
        #outFrame = cv2.putText( outFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        ##outFrame = cv2.rectangle( outFrame, (10,15 - displaySize[0][1]), (10 + displaySize[0][0], 15), (30,30,30), 10)
#        outFrame = cv2.putText( outFrame, displayString, (10,15), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
#
        if showImages:
            cv2.imshow("Frame", outFrame)
            cv2.imshow("Motion", motionFrame)

        if active:
            out.write(outFrame)
        #os.system(settings["clearCommand"])
        #print("cpu: " + str(psutil.cpu_percent()) + " ram: " + str(psutil.virtual_memory().percent))

        #exit when user presses q
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            if not out == None:
                out.release()
            flaskThread.join()
            if not timer == None:
                if timer.is_alive():
                    timer.cancel()
            break     
        time.sleep(settings["loopDelay"])

app=Flask(__name__,static_folder=settings["videoOut"][:-1])
@app.route('/')
def loginPage():
    return render_template('login.html')

@app.route(websiteOffset)
def home():
    global armed
    return render_template('index.html', arm_val = armed)

@app.route(websiteOffset + '/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route(websiteOffset + '/motion_view')
def motion_view():
    return Response(gen_frames_motion(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route(websiteOffset + '/video_records')
def return_videos():
    ret = """
    <!DOCTYPE html>
    <html>
    <body>
    <a href=\"./\">Home</a>
    """

    video_str = """
    <p>{vanity}</p>
    <video height="480" width="640" controls>
        <source src=\"{lbrace}{lbrace} url_for('static', filename=\"{filename}\") {rbrace}{rbrace}\">
    </video>
    <br>
    """
    for filename in reversed(os.listdir(settings["videoOut"])):
        if filename.endswith(".mp4") or filename.endswith(".webm"):
            ret = ret + video_str.format(filename = filename, lbrace = "{", rbrace="}", vanity = filename.replace(".webm", ""))

    ret += """
    </html>
    </body>
    """
    return render_template_string(ret)

@app.route(websiteOffset + "/arm", methods=["POST"])
def onArmButton():
    global armed
    #print("It should arm or unarm now")
    armed = not armed
    if armed:
        print("Armed")
    else:
        print("Disarmed")

    return redirect(websiteOffset)

@app.route("/login", methods=["POST"])
def checkPassword():
    if request.form['password'] == settings["websitePassword"]:
        return redirect(websiteOffset)
    else:
        return "Wrong"


def startApp():
    app.run(host='0.0.0.0', ssl_context='adhoc')

def gen_frames():
    global frame
    global displayString
    global timeString

    while(True):

        #timeInfo = datetime.datetime.now()
        #recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        timeInfo = datetime.datetime.now(tz=timezone)
        recName = timeString
        outFrame = frame
        timeSize = cv2.getTextSize(recName, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        displaySize = cv2.getTextSize(displayString, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        outFrame = cv2.rectangle( outFrame, (10,470 - timeSize[0][1]), (10 + timeSize[0][0], 470), (30,30,30), 10)
        outFrame = cv2.putText( outFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        outFrame = cv2.rectangle( outFrame, (10,15 - displaySize[0][1]), (10 + displaySize[0][0], 15), (30,30,30), 10)
        outFrame = cv2.putText( outFrame, displayString, (10,15), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        ret, buffer = cv2.imencode('.jpg', outFrame)
        out = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + out + b'\r\n')  # concat frame one by one and show result
        time.sleep(settings["loopDelay"])

def gen_frames_motion():
    global motionFrame
    global timeString
    global displayString
    while(True):

        #timeInfo = datetime.datetime.now()
        #recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        timeInfo = datetime.datetime.now()
        recName = timeString
        outFrame = motionFrame
        timeSize = cv2.getTextSize(recName, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        displaySize = cv2.getTextSize(displayString, cv2.FONT_HERSHEY_SIMPLEX, .4, 1)
        outFrame = cv2.rectangle( outFrame, (10,470 - timeSize[0][1]), (10 + timeSize[0][0] - 7, 470), (30,30,30), 10)
        outFrame = cv2.putText( outFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        outFrame = cv2.rectangle( outFrame, (10,15 - displaySize[0][1]), (10 + displaySize[0][0], 15), (30,30,30), 10)
        outFrame = cv2.putText( outFrame, displayString, (10,15), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        ret, buffer = cv2.imencode('.jpg', outFrame)
        out = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + out + b'\r\n')  # concat frame one by one and show result
        time.sleep(settings["loopDelay"])

cameraThread = threading.Thread(target = grabFrames)
cameraThread.start()
ret, frame = cap.read()
motionFrame = getMotion(frame)

while not ret:
    ret, frame = cap.read()
    motionFrame = getMotion(frame)

motionThread = threading.Thread(target = determineMotion)
motionThread.start()

#setStartDelayTimer()
#startDelayTimer.start()
if settings["websiteOn"]:
    flaskThread = threading.Thread(target = startApp)
    flaskThread.start()

main()
