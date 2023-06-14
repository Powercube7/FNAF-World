import json
import time
import pyautogui
import win32process
import psutil
import random
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
        # Check if the user data file exists and if it contains a valid executable path
        assert os.path.isfile("user.json")
        with open("user.json", "r") as f:
            data = json.load(f)
            exePath = data.get("exePath")
            if not os.path.isfile(exePath) or exePath is None:
                raise ValueError

    except (AssertionError, FileNotFoundError):
        # If the user data file is not found, prompt the user to start the game to create a new user data file
        pyautogui.alert(
            title="Alert", text="No user data file found.\nPlease start the game to use this program")
        get_game_path()

    except ValueError:
        # If the user data file is invalid, prompt the user to start the game to create a new user data file
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

    return gameName in processes


class InferenceActions:

    def __init__(self, model):
        """
        Initializes the Inference class with a given model.

        Parameters:
            model (detectron2.engine.defaults.DefaultPredictor): The model to use for inference.
        """
        self.model = model

    def runInference(self, img, returnParams=False):
        """
        Runs the given image through the model and returns the detection results.

        Parameters:
            img (PIL.Image): The image to run through the model.
            returnParams (bool): Whether or not to return the detection details.

        Returns:
            Detectron2.utils.visualizer.GenericMask: The detection results.
            dict: A dictionary containing the detection details (if returnParams is True).
        """

        # Run the image through the model
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

    def getCurrentStatus(self, parametersDict):
        """
        Determines the current status of the game based on the given parameters dictionary.

        Parameters:
        parametersDict (dict): A dictionary containing the detection details of the current game screen.

        Returns:
        str: A string representing the current status of the game.
        """
        statusOptions = {
            'Overworld': 'Overworld',
            'New Challenger': 'Encountered Challenger',
            'Victory': 'Battle End Screen',
            'Health': 'In Battle',
            'Lolbit Shop': 'Shopping'
        }

        return "Picking Option" if all(option in parametersDict["name"] for option in ["Health", "Fighting Option"]) else next((option for label, option in statusOptions.items() if label in parametersDict["name"]), "Clueless")


class Modules:

    def __init__(self) -> None:
        self.previous_key = None
        self.last_seen = None
        self.activated = {
            'AutoRoam': False,
            'AutoFight': False
        }

    def promptModules(self):
        """
        Prompts the user to enable or disable the AutoFight and AutoRoam modules.

        Returns:
        None
        """
        self.activated['AutoFight'] = pyautogui.confirm(
            title="Enable Module", text="Do you want to enable the fighting module?", buttons=["Yes", "No"]) == "Yes"
        self.activated['AutoRoam'] = pyautogui.confirm(
            title="Enable Module", text="Do you want to enable the roaming module?\nWARNING: Having a text prompt open while the module is running will cause the inputs to be sent to the prompt.", buttons=["Yes", "No"]) == "Yes"
        
    def runModules(self, parameters, status):
        """
        Runs the AutoFight and AutoRoam modules if they are enabled.

        Parameters:
            parameters (dict): A dictionary containing the detection details of the current game screen.
            status (str): A string representing the current status of the game.

        Returns:
            None
        """
        if self.activated['AutoFight']:
            self.AutoFight(parameters, status)
        if self.activated['AutoRoam']:
            self.AutoRoam(parameters, status)

    def clickWarp(self, number):
        pyautogui.click(1817, 30 + (number * 110))

    def AutoFight(self, parameters, status):
        """
        Picks a fighting option at random from the available options on the screen.

        Parameters:
            parameters (dict): A dictionary containing the detection details of the current game screen.
            status (str): A string representing the current status of the game.

        Returns:
            None
        """
        if status == 'Picking Option':
            indexes = [i for i, name in enumerate(parameters["name"]) if name == 'Fighting Option']
            option_picked = random.choice(indexes)
            pyautogui.click(parameters["center"][option_picked])

    def AutoRoam(self, parameters, status):
        """
        Moves the player character randomly in the overworld or attempts to return to a known state if the program doesn't know the current status.

        Parameters:
            parameters (dict): A dictionary containing the detection details of the current game screen.
            status (str): A string representing the current status of the game.

        Returns:
            None
        """
        controls = ['w', 'a', 's', 'd']
        if self.last_seen is not None and time.time() - self.last_seen > 30:
            self.clickWarp(random.randint(1, 6))
        else:
            self.last_seen = time.time()

        # Add function to avoid repeating code blocks
        def press(key, delay = None):
            pyautogui.keyDown(key)
            if delay != None:
                time.sleep(delay)
            pyautogui.keyUp(key)

        # If the user is in the overworld, move in a random direction and save the key pressed
        if status == 'Overworld':
            key = random.choice(controls)
            press(key, random.uniform(0, 1.5))
            self.previous_key = key

        elif status == 'Clueless':
            # Keep pressing the previous key until the AI has returned to the overworld, or press a random key if there isn't a previous key
            press(controls[(controls.index(self.previous_key) + 2) % len(controls)] if self.previous_key != None else random.choice(controls), 0.5)

        # If the user enters a shop, click the Done button to exit
        elif status == 'Shopping' and 'Done Button' in parameters['name']:
            pyautogui.click(parameters['center'][parameters['name'].index('Done Button')])