# Description
Welcome to my repository. This is a personal project powered by YOLOv5 that removes the grinding factor of the game by adding a few modules

# Features
The current version features 2 modules:

1) AutoRoam: This module sends random inputs to the game
It has 3 states:
- Clueless: Sends inputs without delay in order to find the character
- Overworld: Sends 0.5 seconds long inputs in order to find battles easier
- Lolbit Shop: Quickly exits out of the shop

2) AutoFight: This module picks a random fighting option when they show up

# Installation instructions
- Install the required dependencies (pip install -r requirements.txt)
- Use the grinder.py file to use the program

# Goals
- Create a pathing system for AutoRoam
- Create a system that picks the options that deal the most damage in AutoFight
- Add the ability to go to certain areas in the game
- Make script easier to use
- Add more ending statistics (e.g. how many new characters, etc.)