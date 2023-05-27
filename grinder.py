try:
    import pyautogui
    import os
    import random
    from PIL.ImageGrab import grab as grabScreenshot
    import functions
    import logging
    import sys
    import json
    import keyboard
    import time
    import torch
except ModuleNotFoundError:
    import os
    import random
    import logging
    import sys
    import json
    os.system("pip install -r requirements.txt")
    import pyautogui
    import functions
    import keyboard
    import time
    import torch

logFile = open("log.txt", "w+")
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=logFile)
logger.addHandler(handler)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    pyautogui.alert(
        text="An error occurred.\nTraceback details saved to log.txt\nPlease report this error to the developer.", title="Error")
    logger.error(msg="An unexpected error occured!",
                 exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def clickWarp(number):
    pyautogui.click(1817, 30 + (number * 110))


previousKey = None
previousStatus = None
victories = 0
challengers = 0

functions.check_user_data()
print("User data found. Starting program...")
if not functions.isGameOpened():

    # Read the exePath from the user data file and save it in the variable "gamePath"
    with open("user.json", "r") as f:
        data = json.load(f)
    gamePath = data.get("exePath")

    try:
        os.startfile(gamePath)
        print("Game opened successfully. Starting modules.")
    except:
        print("Game could not be opened. Please make sure the game is installed and the path is correct.\nIf the path isn't correct, delete user.data and restart the program.")
else:
    print("Game already open. Starting modules.")

# Load the modules
fight, roam = functions.enableModules()
modules = functions.Modules

# Load AI Model
if fight or roam:
    try:
        print("Trying to load AI model from cache...")
        model = torch.hub.load("ultralytics/yolov5", "custom",
                               "./assets/FNAF.pt", verbose=False, _verbose=False)
    except TypeError:
        print("Error occured. Force reloading cache...")
        model = torch.hub.load("ultralytics/yolov5", "custom", "./assets/FNAF.pt",
                               verbose=False, force_reload=True, _verbose=False)
    model.conf = 0.7
    print("\nAI Model loaded successfully")
    yoloActions = functions.InputActions(model)
else:
    pyautogui.alert("No modules enabled. Exiting program.",
                    title="No modules enabled")
    exit()

print(f"Automatic Fighting Engaged: {fight}")
print(f"Automatic Roaming Engaged: {roam}")

start = time.time()
while not keyboard.is_pressed('q'):

    # Take a screenshot of the game and get the status using the AI's detections
    frame = grabScreenshot()
    resultImage, parameters = yoloActions.runInference(frame, True, True)
    currentStatus = yoloActions.getCurrentStatus(parameters)

    # If E is being held, check if switch button and health is visible (prevents clicks during team selection)
    if keyboard.is_pressed('e'):
        if "Switch Button" in parameters["name"] and "Health" in parameters["name"]:
            switchButton = parameters["center"][parameters["name"].index(
                "Switch Button")]
            pyautogui.moveTo(switchButton)
            pyautogui.click()

    # If C is being held, check if the player is in the overworld and click the chips button if that's the case
    elif keyboard.is_pressed('c') and currentStatus == "Overworld":
        chipsButton = pyautogui.center((305, 994, 270, 63))
        pyautogui.moveTo(chipsButton)
        pyautogui.click()

    else:
        # Run actions based on the enabled modules
        if fight:
            modules.AutoFight(parameters, currentStatus)
        if roam:
            # If the current status is different from Clueless, restart the timer
            if currentStatus != "Clueless":
                start = time.time()

            # If the time is greater than 15 seconds, warp to a random location
            if time.time() - start > 15:
                location = random.randint(1, 6)
                clickWarp(location)
                start = time.time()

            previousKey = modules.AutoRoam(
                currentStatus, previousKey, parameters)

        # Increment the total victories if the user won
        if currentStatus == 'Battle End Screen' and previousStatus != currentStatus:
            victories += 1

        # Increment the total challengers if the user encountered one
        if currentStatus == 'Encountered Challenger' and previousStatus != currentStatus:
            challengers += 1

    previousStatus = currentStatus
pyautogui.alert(title="Program ended",
                text=f"Total battles won: {victories}\nTotal challengers encountered: {challengers}")
