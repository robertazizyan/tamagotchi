# A Python Tamagotchi Game

## Requirements
The program makes uses of the following pypi modules:
1. **werkzeug**
2. **pyfiglet**
3. **tabulate**

To install any of those, run 'pip install' + name of the modules above in the terminal window. Note that without any of those modules you'll encounter errors during the program execution.

## Contents

1. project.py - main file for the game
2. database.db - a SQLite3 database with the user and Tamagotchi info
3. saves.csv - a CSV file containing saves for all the Tamagotchi
4. images.py - a file with the Tamagotchi images created with docstrings and ASCII art
5. test_project.py - a testing program
6. database_test.db - a SQLite3 database used for testing purposes


## Description
The program is a terminal-based implementation of the Tamagotchi game with user inputs used as commands to interact with the Tamagotchi.

It involves several actions on par with the original game such as feeding or interacting with your Tamagotchi along with the time-passage feature and a save system (more on those down in the **features section**)

### Launching the program
To launch the game, just move to the project directory and either run the python file or run the command 'python3 project.py'.

### Running the program
The first step is logging in, by providing the username first. If you've previously registered, you'll be prompted to enter your password and choose the Tamagotchi you want to play with, and if not, you'll just need to register and create a new Tamagotchi.

**_IMPORTANT_**
**Even though the database used for saves is only local, DO NOT USE ANY USERNAMES AND/OR PASSWORDS FROM OTHER WEBSITES!!!**

After these steps, you'll be facing the main menu with the indicated row indexes standing for certain actions. This also stands true for other menus such as food and interaction menu. The interaction is straight forward and shouldn't cause any issues when playing the game.

Note that the multiplayer (*at least the one action available for it*) is only local, since both the database and the save file changes are only recorded to the device from where you launch the program for. So if you (_for some unbelievable reason_) want to play the game along with your friends, you'll either have to exchange your whole data sets or use the same versions of the database and the save file.

All the actions you take in the game and their effect on your Tamagotchi will be saved automatically, so don't worry about saving. More on that down below.


## Features
### DB and saves
So first of all the game features a local SQLite3 database that contains the info on users (username and password) and their respective Tamagotchi. Password are saved in a hashed version using the _werkzeug_ module. For the purpose of database integrity don't try to manually change the data in the 'database.db' file as it may ruin the user experience.

The game also runs a local CSV save file called 'saves.csv'. It contains information about the user (username) and Tamagotchi(name, food status, happiness status, birthday, and the time that the Tamagotchi has last been interacted with). Save file is updated automatically after every action when the program runs. And again, take care when and if manually changing the files for some reason. The program runs the csv.DictReader method when accessing the save file, so make sure not to alter the names of the headers for the program to run smoothly.

### Key features
#### Simulating time passage
So the first key feature you'll probably encounter when entering the game for the second time is **simulating time passage**. This means that your Tamagotchi's statuses will linearly decrease based on the time you haven't played or interacted with it and will be recalculated and stored in the save file the moment you choose that exact Tamagotchi. Now the minimum status value is 0, so it won't go below that (and won't really negatively affect your Tamagotchi), but this feature has been implemented for a better interactivity.

#### Proceeding with an action
Another interesting feature associated with the Tamagotchi statuses is determining whether the Tamagotchi will do what you ask it to. This is based on the pseudo-random success chance that changes based on your Tamagotchi statuses, _e.g. having a greater food status will make your Tamagotchi less likely to eat more food._ The actual algorithm used here is subject to change, but overall the feature just adds more interactivity.

#### Visiting a friend
There is an option to visit a friend in the main menu, which will increase the happiness status of both your Tamagotchi and the one you visited. **Note that since the database is local only, you can only visit a friend that is already in your version of the database and your save file only.** This is yet again a subject to change, but as of yet I don't have the skills necessary to host the database and the save file remotely for all for all the users to share.

#### Changing the image of your Tamagotchi
Well this is not a feature really, but you can still do this, since the animation frames for the Tamagotchi are stored in the 'images.py' file. There are two states of the Tamagotchi (egg and the grown up version) with 3 frames each made using ASCII Art and stored in a form of docstrings. So you could change any of those if you wish for your Tamagotchi to look differently (_but make sure to change all the frames and for a smoother animation use the 'image_2' variable as your static picture of your tamagotchi_).

### Restrictions
There are a few rules regarding the user experience listed below:

1. As mentioned someplace above to avoid data loss, **don't fiddle with the db and save files unnecessarily**.
2. The program has a test database 'database_test.db' and a testing program 'test_project.py', that also uses the original save file 'saves.csv' for testing various functions and methods inside the program. To avoid data loss yet again, it's advised to **refrain from using the word '_test_' in your Tamagotchi names**, since running the testing program might delete the save for such a Tamagotchi.

### Final words
Overall this being my first self made _somewhat serious_ Python project made for a CS50p course ever taught me a lot: from firstly considering the general design of the code you'll be writing, to defining its inner structure, and to finally to avoiding **A LOT** of the uneccesary lines by writing support functions or methods, and many more minor things that will make too long of a list to even mention here. This has been a fun and engaging thing to do!

_P.S._
I'm always open to suggestions on how to improve the current state of my program, so anybody reading this is welcome to give me a feedback! Ideas for new features are also welcome (especially on how to set up an actual remote database and save file to actually make this a multiplayer game).

**Thanks for checking this out:)**
