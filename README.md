# FPL Analysis

FPL Analysis is a project under development whose purpose is to assist managers with their Fantasy Premier League team  management.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Suggestions](#suggestions)
- [Known Errors](#known-errors)

## Installation

The program runs on Python 3.10.
1. Install from source on Linux
```bash
$ git clone https://github.com/spym10111/FPLanalysis.git
$ cd fplanalysis
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python3 main.py
```
2. Install from source on Windows
```bash
git clone https://github.com/spym10111/FPLanalysis.git
cd fplanalysis
python -m venv venv
.\venv\scripts\activate
pip install -r requirements.txt
python main.py
```
or download the .zip file directly from GitHub.

## Usage

FPL Analysis automatically creates or updates a Fantasy team for you. The suggestions the program provides are given based on the players' previous FPL performance and are by no means based on their actual game performance. That means that it calculates each player's value based solely on FPL stats, avoiding his actual statistical value as a player, even though it may have an impact in the final comparison with other players. Although not perfect, FPL Analysis can still give a useful insight into the game and provide fast suggestions to FPL managers.

The use is pretty straightforward for now. Just running the main.py opens the main menu.
```
---------------------------------Welcome to FPL Analysis!---------------------------------


Please enter a number from the list below:


1. Sign in to your FPL account: Use your FPL log-in information to get your team.

2. Create new team: The program creates the best possible team for you.

3. Enter new team: You manually enter your team.

4. Open saved team: Open a previously saved team.

5. Rank players.

6. Exit


Enter number:
```
Depending on your choice the program has different functionalities. The options are shown in parentheses.

For example:
```
Do you want to exclude any players (yes/no/suggestion)?
```
The program will first ask for a Gameweek period for which to calculate the optimal suggestions.
```
The program needs to calculate player points based on their stats and upcoming games.
Please enter the GW period for which you want the team to be calculated.

First GW:
Last GW: 
```
The results that the program provides after that stage correspond to that particular period and might not be useful as a whole. You can use its different functionalities according to your preferences. The suggestions the follow are based on our experience using FPL Analysis up to this point.

### Suggestions

- Always run the suggestion option before you finalise your transfer moves in the actual game. The program is not perfect and might show some irregularities from time to time. Please report anything that might seem suspicious to you. Check the known errors section for further information.
- The suggestion option of the program provides suggestions for the given team taking into consideration a -4 hit. Based on that, the "best value probability" given is not an actual probability but rather a performance comparison based on the program's calculations. As the actual probability differs from this "performance comparison" and the odds of an accurate result are slim, up to this point we suggest you use the suggestions option (even if you take the -4 hit) for a percentage of 80% and above for better results. (Be prepared for many hits...)
- The suggestion of a player change might differ from the actual replacement done by the program. The -4 hit calculation used in only one of the two options and not both is to blame for that. This has also shown that based on the FPL Analysis calculations players with better fantasy points output might be better when taking a -4 hit while players with easier games coming up (FDR factor) might be better if you don't.
- FPL Analysis should be used for a better overall season performance. Temporary one Gameweek replacements might not have the expected performance. On that note, please avoid betting real money using our program as a guide. The suggestions that the program provides still have a chance to fail.

## Known Errors

Known errors meant to be fixed hopefully soon. If you don't find your problem here please report it so that we can hopefully fix it.

- The update option changes one player at a time. That means that double player changes might be better due to better budget management even though it doesn't seem so when updating your team. That is why you should always run the suggestion option (both for single and double player changes) even when creating a completely new team.
