# I want to run the settingsInit.py and any maintenence UI stuff here, while main handles starting this up and running camera.
# Need to add making sure video directory exists.
from util import getSettings
import settingsInit

import os

def run():
    print("Initializing settings")
    settingsInit.run()
    settings = getSettings()
    print("Making output file")
    if not os.path.exists(settings["videoOut"]):
        os.mkdir(settings["videoOut"])
