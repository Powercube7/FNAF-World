import psutil
import pyautogui
import time
import random
import cv2
import os

def checkFirstTimeUse():
    if not os.path.exists("user.data"):
        pyautogui.alert(title="Alert", text="User data for first time use not found.\nPlease complete the following prompt to use this program")
        exe_name = pyautogui.prompt(title="Setup", text='Please insert the name of the game exe file (without the .exe extension)')
        
        if exe_name == None:
            pyautogui.alert(title="Alert", text="Setup aborted")
            exit()

        else:
            def find(name, path):
                for root, dirs, files in os.walk(path):
                    if name in files:
                        return os.path.join(root, name)
            print("Searching the C: drive for the game exe file...")
            location =  find(exe_name + ".exe", "C:\\")
            if location == None:
                print("Game exe file not found.")
                pyautogui.alert(title="Alert", text="Game not found. Please restart the program and try again")
                exit()
            else:
                '''
                1. Split the location into a list with the backslash character as a delimiter
                2. If an element has multiple words, surround it with quotation marks
                3. Join the list back together with a backslash
                '''
                print("Game exe file found.")
                location = location.split("\\")
                for i in range(len(location)):
                    if " " in location[i]:
                        location[i] = '"' + location[i] + '"'
                location = "\\".join(location)

                f = open("user.data", "w+")
                f.write(f"exePath={location}\nexeName={exe_name}.exe")
        return False
    else:
        return True

def getCenter(index, parameters):
            x1, x2 = parameters["xmin"][index], parameters["xmax"][index]
            y1, y2 = parameters["ymin"][index], parameters["ymax"][index]

            center = (int((x2 + x1) / 2), int((y2 + y1) / 2))
            return center

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
    enableFighting = pyautogui.confirm(title="Enable Module", text="Do you want to enable the fighting module?", buttons=["Yes", "No"])
    enableRoaming = pyautogui.confirm(title="Enable Module", text="Do you want to enable the roaming module?\nWARNING: Having a text prompt open while the module is running will cause the inputs to be sent to the prompt.", buttons=["Yes", "No"])

    fight = False
    roam = False

    # Enable modules if prompted by the user
    if enableFighting == "Yes":
        fight = True
    if enableRoaming == "Yes":
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

        statusOptions = ['Overworld', 'Encountered Challenger', 'Battle End Screen', 'In Battle', 'Shopping']
        labels = ['Overworld', 'New Challenger', 'Victory', 'Health', 'Lolbit Shop']

        # If nothing is found set the status to "Clueless"
        if parametersDict["name"] == []:
            status = "Clueless"
        # Set the status to Picking Option only if the AI finds both the health of the characters and the fighting option in order to avoid fake positives
        elif "Health" in parametersDict["name"] and "Fighting Option" in parametersDict["name"]:
            status = "Picking Option"
        else:
            # Iterate through the rest of the labels and check if any of them are in the name list. If so, set the status to the option corresponding to that label
            for i in range(0, len(labels)):
                if labels[i] in parametersDict["name"]:
                    status = statusOptions[i]
                    break

        # Set status to Clueless if it's None to avoid errors
        if status == None:
            status = "Clueless"

        # Add the status on an image if the user supplies one
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
        if status == 'Picking Option':
            indexes = []
            for i in range(0, len(parameters["name"])):
                if parameters["name"][i] == 'Fighting Option':
                    indexes.append(i)
            optionPicked = random.choice(indexes)
            pyautogui.click(getCenter(optionPicked, parameters))

    def AutoRoam(status, previous, parameters):
        controls = ['w', 'a', 's', 'd']

        # Add function to avoid repeating code blocks
        def press(key, delay = None):
            pyautogui.keyDown(key)
            if delay != None:
                time.sleep(delay)
            pyautogui.keyUp(key)

        # If the user is in the overworld, update the key value with one of the WASD keys randomly to move around for a random duration of maximum 1.5 seconds
        if status == 'Overworld':
            key = random.choice(controls)
            press(key, random.uniform(0, 1.5))
            previous = key

        # If the program doesn't know the status, press the reverse key in an attempt to return to a known state
        elif status == 'Clueless' and previous != None:
            press(controls[(controls.index(previous) + 2)%len(controls)], 0.5)
        elif status == 'Clueless' and previous == None:
            press(random.choice(controls), 0.5)
                
        # If the user enters a shop, click the Done button
        elif status == 'Shopping':
            location = parameters["name"].index("Done Button")
            if location != -1:
                pyautogui.click(getCenter(location, parameters))

        return previous