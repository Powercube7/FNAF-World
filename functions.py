import json
import time
import pyautogui
import win32process
import psutil
import random
import cv2
import os

def check_user_data():
    """
    Checks if the user data file exists and if it contains a valid executable path to the FNaF World executable.
    If the user data file is not found or is invalid, prompts the user to start the game to create a new user data file.

    Raises:
        FileNotFoundError: If the user data file is not found.
        ValueError: If the user data file contains an invalid executable path.
    """
    try:
        assert os.path.isfile("user.json")
        with open("user.json", "r") as f:
            data = json.load(f)
            exePath = data.get("exePath")
            if not os.path.isfile(exePath) or exePath is None:
                raise ValueError

    except (AssertionError, FileNotFoundError):
        pyautogui.alert(
            title="Alert", text="No user data file found.\nPlease start the game to use this program")
        get_game_path()
    
    except ValueError:
        pyautogui.alert(
            title="Alert", text="The user data file is invalid.\nPlease start the game to use this program")
        get_game_path()


def get_game_path():
    """
    Finds the path to the FNaF World executable and saves it to a user data file.

    Raises:
        Exception: If the executable path is not found.
    """
    hwnd = []

    # Loop until the FNaF World window is found
    while hwnd == []:
        hwnd = pyautogui.getWindowsWithTitle("FNaF World")
        if len(hwnd) > 0:
            hwnd = win32process.GetWindowThreadProcessId(hwnd[0]._hWnd)[1]
            exePath = None

    # Get the process ID of the FNaF World window and find the executable path
    for process in psutil.process_iter():
        try:
            if process.pid == hwnd:
                exePath = process.exe()
                break
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            exePath = None

    # Raise an exception if the executable path is not found
    if exePath is None:
        raise Exception("Could not find FNaF World process")

    # Get the name of the executable and save the path and name to a user data file
    exeName = os.path.basename(exePath)
    data = {"exePath": exePath, "exeName": exeName}
    with open("user.json", "w") as f:
        json.dump(data, f)


def isGameOpened():
    # Get list of current processes using psutil
    processes = [process.name() for process in psutil.process_iter()]

    # Get the name of the game from the user data file
    with open("user.json", "r") as f:
        data = json.load(f)
        gameName = data.get("exeName")

    # Check if the game is opened
    if gameName in processes:
        return True
    else:
        return False


def enableModules():
    # Ask the user if they want to enable the fighting module and the roaming module
    enableFighting = pyautogui.confirm(
        title="Enable Module", text="Do you want to enable the fighting module?", buttons=["Yes", "No"])
    enableRoaming = pyautogui.confirm(
        title="Enable Module", text="Do you want to enable the roaming module?\nWARNING: Having a text prompt open while the module is running will cause the inputs to be sent to the prompt.", buttons=["Yes", "No"])

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

    def runInference(self, img, isBGR=False, returnParams=False):
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
                "center": [(int((box[2] + box[0]) / 2), int((box[3] + box[1]) / 2)) for box in inferenceResults.xyxy[0]],
                "conf": list(inferenceResults.pandas().xyxy[0].confidence),
                "name": list(inferenceResults.pandas().xyxy[0].name)
            }
            return inferenceResults, parameters

        else:
            return inferenceResults

    def getCurrentStatus(self, parametersDict, addText=[]):
        status = None

        statusOptions = ['Overworld', 'Encountered Challenger',
                         'Battle End Screen', 'In Battle', 'Shopping']
        labels = ['Overworld', 'New Challenger',
                  'Victory', 'Health', 'Lolbit Shop']

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
                cv2.putText(addText, f"Status: {status}", (35, 240),
                            cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 3)
            elif status == 'Picking Option':
                cv2.putText(addText, f"Status: {status}", (20, 140),
                            cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 255, 0), 3)
            elif status == 'Battle End Screen':
                cv2.putText(
                    addText, f"Status: {status}", (20, 90), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 0, 0), 3)
            else:
                cv2.putText(addText, f"Status: {status}", (20, 140),
                            cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 255), 3)
        return status


class Modules:

    def AutoFight(parameters, status):
        if status == 'Picking Option':
            indexes = []
            for i in range(0, len(parameters["name"])):
                if parameters["name"][i] == 'Fighting Option':
                    indexes.append(i)
            optionPicked = random.choice(indexes)
            pyautogui.click(parameters["center"][optionPicked])

    def AutoRoam(status, previous, parameters):
        controls = ['w', 'a', 's', 'd']

        # Add function to avoid repeating code blocks
        def press(key, delay=None):
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
        elif status == 'Clueless':
            # Keep pressing the previous key until the AI has returned to the overworld
            if previous != None:
                press(controls[(controls.index(previous) + 2) %
                      len(controls)], 0.5)

            # If there isn't a previous key, press a random key
            else:
                press(random.choice(controls), 0.5)

        # If the user enters a shop, click the Done button
        elif status == 'Shopping':
            location = parameters["name"].index("Done Button")
            if location != -1:
                pyautogui.click(parameters["center"][location])

        return previous
