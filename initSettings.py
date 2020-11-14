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
        "emailAddress",
        "alertEnabled",
        "videoOut",
        "fileNameFormat",
        "showImages",
        "alertMessage",
        "websiteOn",
        "clearCommand"
    ]
    settingsPasswordList = [
        "emailPassword"
    ]
    settingsNumberList = [
        "recordingTime",
        "startDelay",
        "outfileFramerate",
        "loopDelay"
    ]
    settingsListList = [
        "alertGroup"
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