import psutil
import pyautogui
import time
import random
import cv2
import os

def checkFirstTimeUse():
    if not os.path.exists("user.data"):
        file = open("user.data", "w+")
        pyautogui.alert(title="Alert", text="User data for first time use not found.\nPlease complete the following prompt to use this program")
        exe_path = pyautogui.prompt(title="Setup", text='Please insert the location of your FNAF World EXE in the field below.\n\nSteps to get the location:\n1. CTRL+Shift+Right-click your EXE file\n2. Click the "Copy as path" option and paste the output here\n\nWARNING: Inserting the wrong data will lead the program into an unusable state. To fix it delete user.data and redo this process')
        if exe_path != None:
            exe_path = exe_path[1:-1]
            exe_path = exe_path.split("\\")

            file.write("exePath=")

            editedPath = ""
            for directory in exe_path:
                if ' ' in directory:
                    directory = f'"{directory}"'
                editedPath = editedPath + f"{directory}\\"
            file.write(editedPath[:-1])
            file.write(f"\nexeName={exe_path[-1]}")
            file.close()
        else:
            file.close()
            os.remove("user.data")

        return False
    else:
        return True

def isGameOpened():
    processList = psutil.process_iter(attrs=['pid', 'name'])

    gameName = open("user.data", "r")
    gameName = gameName.read()
    gameName = gameName.split("\n")[-1]
    gameName = gameName.replace("exeName=", "")

    gameOpen = False

    for process in processList:
        if process.name() == gameName:
            gameOpen = True
            break
    
    return gameOpen

def enableModules():
    enableFighting = pyautogui.confirm(text="Enable Fighting Module?", title="Module Prompt", buttons=["Yes", "No"])
    enableRoaming = pyautogui.confirm(text="Enable Roaming Module?", title="Module Prompt", buttons=["Yes", "No"])

    if enableFighting.upper() == "YES":
        fight = True
    else:
        fight = False

    if enableRoaming.upper() == "YES":
        roam = True
    else:
        roam = False

    return fight, roam

class InputActions:
    def __init__(self, model):
        self.model = model
    
    def runInference(self, img, isBGR = False, returnParams = False):
        inferenceResults = None
        if not isBGR:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            inferenceResults = self.model(img)
        else:
            inferenceResults = self.model(img)

        if returnParams:
            parameters = {
                "ymax": list(inferenceResults.pandas().xyxy[0].ymax),
                "ymin": list(inferenceResults.pandas().xyxy[0].ymin),
                "conf": list(inferenceResults.pandas().xyxy[0].confidence),
                "xmax": list(inferenceResults.pandas().xyxy[0].xmax),
                "xmin": list(inferenceResults.pandas().xyxy[0].xmin),
                "name": list(inferenceResults.pandas().xyxy[0].name)
            }
            return inferenceResults, parameters
        
        else:
            return inferenceResults
            
    def getCurrentStatus(self, parametersDict, addText = []):
        status = None

        statusOptions = ['Battle End Screen', 'In Battle', 'Overworld', 'Shopping']
        labels = ['Victory', 'Health', 'Overworld', 'Lolbit Shop']

        if parametersDict["name"] == []:
            status = "Clueless"
        elif "Health" in parametersDict["name"] and "Fighting Option" in parametersDict["name"]:
            status = "Picking Option"
        else:
            for i in range(0, len(labels)):
                if labels[i] in parametersDict["name"]:
                    status = statusOptions[i]
                    break

        if status == None:
            status = "Clueless"

        if len(addText) != 0:
            if status == 'Overworld' or status == 'Clueless':
                cv2.putText(addText, f"Status: {status}", (35, 240), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 3)
            elif status == 'Picking Option':
                cv2.putText(addText, f"Status: {status}", (20, 140), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 255, 0), 3)
            elif status == 'Battle End Screen':
                cv2.putText(addText, f"Status: {status}", (20, 90), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 0, 0), 3)
            else:
                cv2.putText(addText, f"Status: {status}", (20, 140), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 3)
        return status

class Modules:

    def AutoFight(parameters, status):
        def getCenter(index):
            x1, x2 = parameters["xmin"][index], parameters["xmax"][index]
            y1, y2 = parameters["ymin"][index], parameters["ymax"][index]

            center = (int((x2 + x1) / 2), int((y2 + y1) / 2))
            return center

        if status == 'Picking Option':
            indexes = []
            for i in range(0, len(parameters["name"])):
                if parameters["name"][i] == 'Fighting Option':
                    indexes.append(i)
            optionPicked = random.choice(indexes)
            pyautogui.click(getCenter(optionPicked))

    def AutoRoam(status, key, previous):
        def press(key, delay = None):
            pyautogui.keyDown(key)
            if delay != None:
                time.sleep(delay)
            pyautogui.keyUp(key)

        if status == 'Overworld':
            previous = key
            while key == previous:
                key = random.choice(['w', 'a', 's', 'd'])
            press(key, 0.5)
                
        elif status == 'Shopping':
            pyautogui.click(1695, 1000)

        elif status == 'Clueless':
            previous = key
            while key == previous:
                key = random.choice(['w', 'a', 's', 'd'])
            press(key)