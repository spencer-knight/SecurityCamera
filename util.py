import json

def getSettings():

    settingsFile = open("settings.json", "r")
    contents = settingsFile.read()
    settingsFile.close()
    settings = json.loads( contents)

    return settings