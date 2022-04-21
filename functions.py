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
            '''
            1. Delete the first and last character of the string
            2. Split the string by the "\\" character
            3. Save the last element of the list in the file under the name "exeName"
            4. If an element has multiple words, put quotation marks around it
            5. Join the string back together with the "\\" character and save it under the name "exePath"
            '''
            exe_path = exe_path[1:-1]
            exe_path = exe_path.split("\\")
            exe_name = exe_path[-1]
            for i in range(len(exe_path)):
                if " " in exe_path[i]:
                    exe_path[i] = f'"{exe_path[i]}"'
            exe_path = "\\".join(exe_path)
            file.write(f"exePath={exe_path}\nexeName={exe_name}")
            file.close()
        else:
            file.close()
            os.remove("user.data")

        return False
    else:
        return True

def isGameOpened():
    # Get list of current processes using psutil
    processes = [process.name() for process in psutil.process_iter()]

    # Get the name of the game from the user data file
    f = open("user.data", "r")
    gameName = f.read()
    gameName = gameName.split("\n")[1]
    gameName = gameName.replace("exeName=", "")
    f.close()

    # Check if the game is opened
    if gameName in processes:
        return True
    else:
        return False
def enableModules():
    # Ask the user if they want to enable the fighting module and the roaming module
    enableFighting = pyautogui.confirm(title="Enable Module", text="Do you want to enable the fighting module?\nNOTE: Enabling the fighting module will cause the program to automatically fight enemies.", buttons=["Yes", "No"])
    enableRoaming = pyautogui.confirm(title="Enable Module", text="Do you want to enable the roaming module?\nNOTE: Enabling the roaming module will cause the program to automatically roam around the map.\nWARNING: Having a text prompt open while the module is running will cause the inputs to be sent to the prompt.", buttons=["Yes", "No"])

    fight = False
    roam = False

    # If the user wants to enable the module, enable it
    if enableFighting:
        fight = True
    if enableRoaming:
        roam = True

    return fight, roam

class InputActions:
    def __init__(self, model):
        self.model = model
    
    def runInference(self, img, isBGR = False, returnParams = False):
        inferenceResults = None

        # Make sure the image is in BGR format for better results
        if not isBGR:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            inferenceResults = self.model(img)
        else:
            inferenceResults = self.model(img)

        # Return the detection details if prompted by the user
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

        # Set status to Clueless to avoid errors
        if status == None:
            status = "Clueless"

        # Add the status on an image if it's passed
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
        # Add function to avoid repeating code blocks
        def press(key, delay = None):
            pyautogui.keyDown(key)
            if delay != None:
                time.sleep(delay)
            pyautogui.keyUp(key)

        # If the user is in the overworld, update the key value with one of the WASD keys randomly to move around for a random duration of maximum 1 second
        if status == 'Overworld':
            key = random.choice(['w', 'a', 's', 'd'])
            press(key, random.random())
            previous = key

        # If the program doesn't know the status, press the previous key for 0.5 seconds
        elif status == 'Clueless':
            press(previous, 0.5)
                
        # If the user enters a shop, click the DONE button
        elif status == 'Shopping':
            pyautogui.click(1695, 1000)