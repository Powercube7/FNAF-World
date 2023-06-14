try:
    import pyautogui
    import os, sys, logging
    import time
    from PIL.ImageGrab import grab as grabScreenshot
    import torch, keyboard
    import functions
    import json
except ModuleNotFoundError:
    import os
    os.system("pip install -r requirements.txt")
    import pyautogui
    pyautogui.alert("The required dependencies have been installed.\nPlease restart the program.", title="Modules Installed")
    exit()

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

previousKey = None
previousStatus = None
victories = 0
challengers = 0

functions.check_user_data()
print("User data found. Starting program...")
if not functions.isGameOpened():
    gamePath = json.load(open("user.json", "r")).get("exePath")
    os.startfile(gamePath)
    print("Game opened successfully. Starting modules.")
else:
    print("Game already open. Starting modules.")

# Load the modules
modules = functions.Modules()
modules.promptModules()

# Load AI Model
if True in modules.activated.values():
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
    yoloActions = functions.InferenceActions(model)
else:
    pyautogui.alert("No modules enabled. Exiting program.",
                    title="No modules enabled")
    exit()

print(f"Automatic Fighting Engaged: {modules.activated['AutoFight']}")
print(f"Automatic Roaming Engaged: {modules.activated['AutoRoam']}")

start = time.time()
while not keyboard.is_pressed('q'):

    # Take a screenshot of the game and get the status using the AI's detections
    frame = grabScreenshot()
    resultImage, parameters = yoloActions.runInference(frame, True)
    currentStatus = yoloActions.getCurrentStatus(parameters)

    # If E is being held, check if switch button and health is visible (prevents clicks during team selection)
    if keyboard.is_pressed('e'):
        if "Switch Button" in parameters["name"] and "Health" in parameters["name"]:
            switchButton = parameters["center"][parameters["name"].index("Switch Button")]
            pyautogui.moveTo(switchButton)
            pyautogui.click()

    # If C is being held, check if the player is in the overworld and click the chips button if that's the case
    elif keyboard.is_pressed('c') and currentStatus == "Overworld":
        chipsButton = pyautogui.center((305, 994, 270, 63))
        pyautogui.moveTo(chipsButton)
        pyautogui.click()

    else:
        # Run actions based on the enabled modules
        modules.runModules(parameters, currentStatus)

        # Increment the total victories if the user won
        if currentStatus == 'Battle End Screen' and previousStatus != currentStatus:
            victories += 1

        # Increment the total challengers if the user encountered one
        if currentStatus == 'Encountered Challenger' and previousStatus != currentStatus:
            challengers += 1

    previousStatus = currentStatus

pyautogui.alert(title="Program ended",
                text=f"Total battles won: {victories}\nTotal challengers encountered: {challengers}")
