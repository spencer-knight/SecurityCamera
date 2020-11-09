import json

def getSettings():

    settingsFile = open("settings.json", "r")
    settings = json.loads( settingsFile.read())

    return settings