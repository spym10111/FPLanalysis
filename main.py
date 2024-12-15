from fplteam import FPLteam
import time
import logos

logos.print_header()


def menu() -> None:
    """
    Starting menu of the program.

    :return: None
    """
    choice = 0
    while choice not in [1, 2, 3, 4, 5]:
        print("\n\n-------------------------------------Main Menu------------------------------------"
              "-----------------")
        print("\nPlease enter a number from the list below: ")
        print("\n\n1. Sign in to your FPL account: Use your FPL log-in information to get your team.")
        print("\n2. Create new team: The program creates the best possible team for you.")
        print("\n3. Enter new team: You manually enter your team.")
        print("\n4. Open saved team: Open a previously saved team.")
        print("\n5. Rank players.")
        print("\n6. Exit")

        choice = pick_menu_number()
        print("")
        if choice == 1:
            try:
                fplteam = FPLteam()
                try:
                    # Using log-in information
                    fplteam.open_user_team()
                    fplteam.print_result()
                    fplteam.transfer_players()
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                print("Unfortunately, the FPL official game is updating. The program will now exit. "
                      "\nThank you for using FPL Analysis. Please come back later.")
                time.sleep(7)
                break
        elif choice == 2:
            try:
                fplteam = FPLteam()
                try:
                    # Creating the best team without any inputs
                    fplteam.create_new_team()
                    fplteam.transfer_players()
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                print("Unfortunately, the FPL official game is updating. The program will now exit. "
                      "\nThank you for using FPL Analysis. Please come back later.")
                time.sleep(7)
                break
        elif choice == 3:
            try:
                fplteam = FPLteam()
                try:
                    # Creating a new team by entering names
                    fplteam.enter_new_team()
                    fplteam.print_result()
                    fplteam.transfer_players()
                    fplteam.save_team()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                print("Unfortunately, the FPL official game is updating. The program will now exit. "
                      "\nThank you for using FPL Analysis. Please come back later.")
                time.sleep(7)
                break
        elif choice == 4:
            try:
                fplteam = FPLteam()
                try:
                    # Using a previously saved team
                    fplteam.open_saved_team()
                    fplteam.print_result()
                    fplteam.transfer_players()
                    fplteam.save_team()
                except FileNotFoundError:
                    print("\nThere is no previously saved team.")
                    choice = 0
                    continue
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                print("Unfortunately, the FPL official game is updating. The program will now exit. "
                      "\nThank you for using FPL Analysis. Please come back later.")
                time.sleep(7)
                break
        elif choice == 5:
            try:
                fplteam = FPLteam()
                try:
                    # Comparing players' captaincy points
                    fplteam.compare_players()
                except ValueError:
                    choice = 0
                    continue
            except NotImplementedError:
                print("Unfortunately, the FPL official game is updating. The program will now exit. "
                      "\nThank you for using FPL Analysis. Please come back later.")
                time.sleep(7)
                break
        elif choice == 6:
            # Exits the program
            print("\nThank you for using FPL Analysis.")
            time.sleep(2)
            break
        choice = 0


def pick_menu_number() -> int:
    """
    Gets the menu choice of the user.

    :return: int
    """
    choice = ""
    while choice not in [1, 2, 3, 4, 5, 6]:
        try:
            choice = int(input("\n\nEnter number: "))
            if choice not in [1, 2, 3, 4, 5, 6]:
                print("\nInvalid number.")
        except ValueError:
            print("\nInvalid number.")
            choice = ""
    return choice


menu()
