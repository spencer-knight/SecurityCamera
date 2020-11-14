import json
import pip._internal as pip

def getSettings():

    try:
        settingsFile = open("settings.json", "r")
        contents = settingsFile.read()
        settingsFile.close()
        settings = json.loads( contents)
    except IOError:
        file = open("settings.json", "x")
        file.close()
        file = open("settings.json", "w")
        file.write("{}")
        file.close()
        settingsFile = open("settings.json", "r")
        contents = settingsFile.read()
        settingsFile.close()
        settings = json.loads( contents)

    return settings

def install(name):
    pip.main(['install', name])