import requests.exceptions

import fplapi
from fplteam import FPLteam
import time
import logos
from getpass import getpass


def menu() -> None:
    """
    Starting menu of the program

    :return: None
    """
    print("\n\n---------------------------------------Login--------------------------------------"
          "-----------------")
    choice = 0
    credentials = []
    try:
        # Logging in
        credentials = log_in()
    except NotImplementedError:
        updating_delay()
        choice = 6
    except requests.exceptions.ConnectionError:
        connectivity_delay()
        choice = 6

    while choice not in [1, 2, 3, 4, 5, 6, 7]:
        print("\n\n-------------------------------------Main Menu------------------------------------"
              "-----------------")
        print("\nPlease enter a number from the list below: ")
        print("\n\n1. Sign in to your FPL account: Use your FPL log-in information to get your team.")
        print("\n2. Free Hit: Get your Free Hit team.")
        print("\n3. Wildcard/Starting team: The program creates the best possible team for you.")
        print("\n4. Enter new team: You manually enter your team.")
        print("\n5. Open saved team: Open a previously saved team.")
        print("\n6. Rank players: Ranks the given players.")
        print("\n7. Log out.")
        print("\n8. Exit")

        choice = pick_menu_number()
        print("")
        if choice == 1:
            try:
                print("\n\n-----------------------------------Official Team----------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Using log-in information
                    fplteam.open_user_team(credentials[0], credentials[1])
                    fplteam.print_result()
                    fplteam.transfer_players(mode="normal")
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 2:
            try:
                print("\n\n--------------------------------Free Hit------------------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Creates the best Free Hit team
                    fplteam.free_hit(credentials[0], credentials[1])
                    fplteam.transfer_players(mode="free_hit")
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break

        elif choice == 3:
            try:
                print("\n\n----------------------------------New Team (Auto)---------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Creating the best team without any inputs
                    fplteam.create_new_team(credentials[0], credentials[1])
                    fplteam.transfer_players(mode="normal")
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 4:
            try:
                print("\n\n---------------------------------New Team (Manual)--------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Creating a new team by entering names
                    fplteam.enter_new_team()
                    fplteam.print_result()
                    fplteam.transfer_players(mode="normal")
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 5:
            try:
                print("\n\n------------------------------------Saved Team------------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Using a previously saved team
                    fplteam.open_saved_team()
                    fplteam.print_result()
                    fplteam.transfer_players(mode="normal")
                    fplteam.save_team()
                except FileNotFoundError:
                    print("\nThere is no previously saved team.")
                    choice = 0
                    continue
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 6:
            try:
                print("\n\n--------------------------------Player Comparison---------------------------------"
                      "-----------------")
                fplteam = FPLteam()
                try:
                    # Comparing players' captaincy points
                    fplteam.compare_players()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 7:
            try:
                print("\n\n---------------------------------------Login--------------------------------------"
                      "-----------------")
                # Logging in again
                credentials = log_in()
            except NotImplementedError:
                updating_delay()
                break
        elif choice == 8:
            # Exits the program
            print("\n\n---------------------------------------Exit---------------------------------------"
                  "-----------------")
            print("\nThank you for using FPL Analysis.")
            time.sleep(1)
            print("3...")
            time.sleep(1)
            print("2...")
            time.sleep(1)
            print("1...")
            time.sleep(1)
            break
        choice = 0


def pick_menu_number() -> int:
    """
    Gets the menu choice of the user

    :return: int
    """
    choice = ""
    while choice not in [1, 2, 3, 4, 5, 6, 7, 8]:
        try:
            choice = int(input("\n\nEnter number: "))
            if choice not in [1, 2, 3, 4, 5, 6, 7, 8]:
                print("\nInvalid number.")
        except ValueError:
            print("\nInvalid number.")
            choice = ""
    return choice


def updating_delay() -> None:
    """
    Gives an exit sequence in case the game is updating

    :return: None
    """
    print("\nUnfortunately, the FPL official game is updating. The program will now exit. "
          "\nThank you for using FPL Analysis. Please come back later.")
    time.sleep(2)
    print("5...")
    time.sleep(1)
    print("4...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)


def connectivity_delay() -> None:
    """
        Gives an exit sequence in case of connection problem

        :return: None
        """
    print("\nThere is a connection problem. Please check your internet connection and try again."
          "\nThank you for using FPL Analysis.")
    time.sleep(2)
    print("5...")
    time.sleep(1)
    print("4...")
    time.sleep(1)
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)


def log_in() -> list:
    """
    Holds the credentials to an official FPL account

    :return: A list of the username and password of the input
    """
    print("\nPlease enter your official FPL credentials.")
    log_in_info = []
    status_raise = True
    while status_raise:
        try:
            username = user_get_username()
            password = user_get_password()

            fplapi.check_status(username, password)
            log_in_info = [username, password]

            status_raise = False
        except TypeError:
            print("\nInvalid e-mail or password.")
    return log_in_info


def user_get_username() -> str:
    """
    Gets the username of the user's official FPL account

    :return: A string of the user's username
    """
    username = input("\nE-mail: ")
    return username


def user_get_password() -> str:
    """
    Gets the password of the user's official FPL account

    :return: A string of the user's password
    """
    password = getpass("\nPassword: ")
    return password


logos.print_header()
menu()
