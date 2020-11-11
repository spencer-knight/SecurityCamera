import json
import util

settingsFileJson = util.getSettings()
#Can't figure out how to get list input to actually translate


settingsJson = """{
    "emailAddress" : "",
    "emailPassword" : "", 
    "alertEnabled" : false,
    "videoOut" : "./Recordings/",

    
    "alertGroup" : [
        "",
        ""
    ]
}"""
settingsJson = json.loads(settingsJson)
settingList = [
    "emailAddress",
    "emailPassword",
    "alertEnabled",
    "videoOut",
    "testVariable"
]


for item in settingList:
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

with open("settings.json", "w") as out:
    json.dump(settingsJson, out, indent=4)