import json
import util
import getpass

def run():
    settingsFileJson = util.getSettings()
    #Can't figure out how to get list input to actually translate

    settingsJson = json.loads("""{}""")
    defaultsJson = json.loads("""{
        \"videoOut\": \"../Recordings/\",
        \"fileNameFormat\": \"%d-%m-%Y_%H%M\",
        \"showImages\": false,
        \"websiteOn\": true
    }""")
    settingsList = [
        "emailAddress", #email to send alerts from
        "alertEnabled", #whether or not to send alerts
        "videoOut", #location of the video files recorded example: ../Recordings/
        "fileNameFormat", #date format for filename https://www.tutorialkart.com/python/python-datetime/python-datetime-format/
        "showImages", #whether or not to show the images
        "alertMessage", #message sent in alert email
        "websiteOn", #whether or not to run the website
        "clearCommand", #not used anymore but os specific clear cmd
        "timeZone", #IANA timezone
        "websiteOffset", #all website pages will be based on this directory so that no rando can easily look at your camera.
        "websitePassword"
    ]
    settingsPasswordList = [
        "emailPassword" #sender email passowrd
    ]
    settingsNumberList = [
        "recordingTime", #how long after motion is detected that the frames will keep getting written to a file
        "startDelay", #how long after starting to arm
        "outfileFramerate", #framerate of out files
        "loopDelay" #delay in program looops
    ]
    settingsListList = [
        "alertGroup" #list of emails to send alert to, /stop to stop prompting
    ]
    #need to implement way of making this list get taken as input


    for item in settingsList:
        if item in settingsFileJson:
            settingsJson[item] = settingsFileJson[item]
        else:
            if item in defaultsJson:
                settingsJson[item] = defaultsJson[item]
            else:
                userIn = input(item+ ": ")

                userIn = userIn.strip()
                if (userIn == "true" or userIn == "yes") or userIn == "y":
                    settingsJson[item] = True
                else: 
                    if (userIn == "false" or userIn == "no") or userIn == "n":
                        settingsJson[item] = False
                    else:
                        settingsJson[item] = userIn

    for item in settingsPasswordList:
        if item in settingsFileJson:
            settingsJson[item] = settingsFileJson[item]
        else:
            userIn = getpass.getpass(prompt = item + ": ")
            settingsJson[item] = userIn
            #NEED to encrypt this

    for item in settingsNumberList:
        if item in settingsFileJson:
            settingsJson[item] = settingsFileJson[item]
        else:
            if item in defaultsJson:
                seetingsJson[item] = defaultsJson[item]
            else:
                userIn = input(item + ": ")
                settingsJson[item] = float(userIn)

    outList = []
    for item in settingsListList:
        if item in settingsFileJson:
            settingsJson[item] = settingsFileJson[item]
        else:
            if item in defaultsJson:
                seetingsJson[item] = defaultsJson[item]
            else:
                while True:
                    userIn = input(item + ": ")
                    if userIn == "/stop":
                        break
                    outList += [userIn]
            settingsJson[item] = outList
                    
    


    with open("settings.json", "w") as out:
        json.dump(settingsJson, out, indent=4)