import cv2
import threading
import notifacation
import util
import datetime
import json
from flask import Flask, render_template, render_template_string, Response
import time
import os
import psutil



settings = util.getSettings()
startDelay = settings["startDelay"]
recordingTime = settings["recordingTime"]
showImages = settings["showImages"]

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

# Run once the recording timer stops, this means it is the end of the recording period.
def onTimer():
    global active
    active = False
    print("Stop doing")
    out.release()

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
        active = True
        resetTimer()
        setTimer()
        timer.start()
        timeInfo = datetime.datetime.now()
        recName = timeInfo.strftime(settings["fileNameFormat"])
        #might add check to see if file already exists, then add something so that stuff doesn't get overwritten
        out = cv2.VideoWriter(settings["videoOut"] + recName + ".webm",cv2.VideoWriter_fourcc(*"VP80"), settings["outfileFramerate"], (640,480))#
    else: 
        if active and armed:
            resetTimer()
            setTimer()
            timer.start()

def get_performance():
    return "cpu: " + str(psutil.cpu_percent()) + " ram: " + str(psutil.virtual_memory().percent)

def main():
    global frame
    global motionFrame

    while 1:
        ret, frame = cap.read()
        #frame = cv2.resize( frame, (640,480))
        motionFrame = getMotion( frame)
        motionDetectedBool = percentWhite( frame, motionFrame) > 4.0
    
        if motionDetectedBool:
            motionDetected()
            motionFrame = cv2.putText( motionFrame, "Motion Detected", (10,22), cv2.FONT_HERSHEY_SIMPLEX, .7, (100,100,100), 1)


        timeInfo = datetime.datetime.now()
        recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        outFrame = cv2.putText( outFrame, get_performance(), (10,15), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

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

app=Flask(__name__,static_folder='Recordings')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motion_view')
def motion_view():
    return Response(gen_frames_motion(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_records')
def return_videos():
    ret = """
    <!DOCTYPE html>
    <html>
    <body>
    """

    video_str = """
    <p>{vanity}</p>
    <video height="480" width="640" controls>
        <source src=\"{lbrace}{lbrace} url_for('static', filename=\"{filename}\") {rbrace}{rbrace}\">
    </video>
    <br>
    """
    for filename in reversed(os.listdir("./Recordings/")):
        if filename.endswith(".mp4") or filename.endswith(".webm"):
            ret = ret + video_str.format(filename = filename, lbrace = "{", rbrace="}", vanity = filename.replace(".webm", ""))

    ret += """
    </html>
    </body>
    """
    return render_template_string(ret)

@app.route("/test")
def test():
    ret = """
    <!DOCTYPE html>
    <html>
    <body>
    """

    video_str = """
    <video height="480" width="640" controls>
        <source src=\"{lbrace}{lbrace} url_for('static', filename='{filename}') {rbrace}{rbrace}\" type=\"video/mp4\">
    </video>
    <br>
    """
    ret += video_str
    ret += """
    </html>
    </body>
    """
    return render_template_string( ret.format(filename = "rick.mp4", lbrace = "{", rbrace = "}"))
def startApp():
    app.run(host='0.0.0.0')

def gen_frames():
    global frame
    while(True):

        #timeInfo = datetime.datetime.now()
        #recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        #timeInfo = datetime.datetime.now()
        #recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        #outFrame = cv2.putText( outFrame, get_performance(), (10,15), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        out = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + out + b'\r\n')  # concat frame one by one and show result
        time.sleep(settings["loopDelay"])

def gen_frames_motion():
    global motionFrame
    while(True):

        #timeInfo = datetime.datetime.now()
        #recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #outFrame = cv2.putText( frame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        timeInfo = datetime.datetime.now()
        recName = timeInfo.strftime("%a %d/%m/%Y %I:%M:%S %Z")
        #motionFrame = cv2.putText( motionFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)
        #outFrame = cv2.putText( motionFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1)

        ret, buffer = cv2.imencode('.jpg', cv2.putText( motionFrame, recName, (10,470), cv2.FONT_HERSHEY_SIMPLEX, .4, (250,250,250), 1))
        out = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + out + b'\r\n')  # concat frame one by one and show result
        time.sleep(settings["loopDelay"])
setStartDelayTimer()
startDelayTimer.start()
if settings["websiteOn"]:
    flaskThread = threading.Thread(target = startApp)
    flaskThread.start()
main()
