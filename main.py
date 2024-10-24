from fplteam import FPLteam


print("\n---------------------------Welcome to the FPL team creation program!---------------------------")


def menu():
    choice = 0
    while choice not in [1, 2, 3, 4, 5]:
        print("\n\nPlease enter a number from the list below: ")
        print("\n\n1. Sign in to your FPL account: Use your FPL log-in information to get your team.")
        print("\n2. Create new team: The program creates the best possible team for you.")
        print("\n3. Enter new team: You manually enter your team.")
        print("\n4. Open saved team: Open a previously saved team.")
        print("\n5. Exit")

        choice = pick_menu_number()
        print("")
        if choice == 1:
            fplteam = FPLteam()
            try:
                # Using log-in information
                fplteam.open_user_team()
                fplteam.print_result()
                fplteam.transfer_players()
            except ValueError:
                choice = 0
                continue
        elif choice == 2:
            fplteam = FPLteam()
            try:
                # Creating the best team without any inputs
                fplteam.create_new_team()
                fplteam.transfer_players()
            except ValueError:
                choice = 0
                continue
        elif choice == 3:
            fplteam = FPLteam()
            try:
                # Creating a new team by entering names
                fplteam.enter_new_team()
                fplteam.print_result()
                fplteam.transfer_players()
            except ValueError:
                choice = 0
                continue
        elif choice == 4:
            fplteam = FPLteam()
            try:
                # Using a previously saved team
                fplteam.open_saved_team()
                fplteam.print_result()
                fplteam.transfer_players()
            except FileNotFoundError:
                print("\nThere in no previously saved team.")
                choice = 0
                continue
            except ValueError:
                choice = 0
                continue
        elif choice == 5:
            # Exits the program
            print("\nThank you for using the program.")
            break
        choice = 0


def pick_menu_number():
    choice = ""
    while choice not in [1, 2, 3, 4, 5]:
        try:
            choice = int(input("\n\nEnter number: "))
            if choice not in [1, 2, 3, 4, 5]:
                print("\nInvalid number.")
        except ValueError:
            print("\nInvalid number.")
            choice = ""
    return choice


menu()
