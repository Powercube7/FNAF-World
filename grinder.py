import pyautogui
import os
from PIL.ImageGrab import grab as grabScreenshot
import functions
import keyboard
import torch

key = None
previousKey = None
previousStatus = None
totalVictories = 0

if functions.checkFirstTimeUse():
    print("User Data found. Starting program...")
    if not functions.isGameOpened():
        print("Game process not found. Starting game...")
        f = open("user.data", "r")
        gamePath = f.read()
        gamePath = gamePath.split("\n")[0]
        gamePath = gamePath.replace("exePath=", "")

        os.system(f"start {gamePath}")
        print("Game opened successfully. Starting modules.")
    else:
        print("Game already open. Starting modules.")
    fight, roam = functions.enableModules()
    modules = functions.Modules

    model = torch.hub.load("ultralytics/yolov5", "custom", "FNAF.pt")
    model.conf = 0.7
    print("\nAI Model loaded successfully")
    yoloActions = functions.InputActions(model)

    print(f"Automatic Fighting Engaged: {fight}")
    print(f"Automatic Roaming Engaged: {roam}")
    while not keyboard.is_pressed('q'):

        frame = grabScreenshot()
        resultImage, parameters = yoloActions.runInference(frame, True, True)
        currentStatus = yoloActions.getCurrentStatus(parameters)

        if fight:
            modules.AutoFight(parameters, currentStatus)
        if roam:
            modules.AutoRoam(currentStatus, key, previousKey)

        if currentStatus == 'Battle End Screen' and previousStatus != currentStatus:
                totalVictories += 1
        previousStatus = currentStatus

    pyautogui.alert(title="Module ended", text= f"Total battles won: {totalVictories}")
else:
    pyautogui.alert(title="Alert", text="Please restart this program in order to use the updated user data")