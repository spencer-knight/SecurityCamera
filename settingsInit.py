import json
import util

settingsFileJson = util.getSettings()
#Can't figure out how to get list input to actually translate

settingsJson = json.loads("{}")
settingsList = [
    "emailAddress",
    "emailPassword",
    "alertEnabled",
    "videoOut",
    "fileNameFormat",
    "showImages",
    "alertMessage",
    "websiteOn",
    "clearCommand"
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
        userIn = input(item+ ": ")

        if userIn == "true":
            settingsJson[item] = True
        if userIn == "false":
            settingsJson[item] = False
        else:
            settingsJson[item] = userIn

for item in settingsNumberList:
    if item in settingsFileJson:
        settingsJson[item] = settingsFileJson[item]
    else:
        userIn = input(item + ": ")
        settingsJson[item] = float(userIn)

for item in settingsListList:
    if item in settingsFileJson:
        settingsJson[item] = settingsFileJson[item]

with open("settings.json", "w") as out:
    json.dump(settingsJson, out, indent=4)