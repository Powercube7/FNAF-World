# Description
Welcome to my repository. This is a personal project powered by YOLOv5 that removes the grinding factor of the game by adding a few modules

# Features
The current version features 2 modules:

1) AutoRoam: This module sends random inputs to the game
It has 3 states:
- Clueless: Sends the reverse of the last direction in order to locate the lost character
- Overworld: Sends random movement inputs for a maximum of 1.5 seconds in order to find battles
- Lolbit Shop: Quickly exits out of the shop by pressing the done button once found

2) AutoFight: This module picks a random fighting option when they show up

# Additional Controls
- Press Q or close the game to quit the program
- Press E to attempt to switch teams (only works in battle)
- Press C to attempt to open the chips menu (only works in the overworld)

# Installation instructions
- Have FNAF World installed
- Install the required dependencies (pip install -r requirements.txt)
- Use the Run Autopilot.bat file to use the program

# Goals
- Create a pathing system for AutoRoam
- Create a system that picks the options that deal the most damage in AutoFight
- Add the ability to go automatically to certain areas in the game
- Make script easier to use
- Add more ending statistics (e.g. how many tokens earned, how much EXP earned, etc.)
- Make the script more efficient
- Make the program into an executable
- Create a GUI
