# FPL Analysis

FPL Analysis is a project under development whose purpose is to assist managers with their Fantasy Premier League team  management.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Suggestions](#suggestions)

## Installation

The program runs on Python 3.10.

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

5. Exit


Enter number:
```
Depending on your choice the program has different functionalities. The options are shown in parentheses.

For instance:
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
### Suggestions


