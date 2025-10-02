from fplstats import FPLstats
from itertools import combinations
from unidecode import unidecode
from datetime import datetime
import json
from getpass import getpass


class FPLteam:
    """
    Holds the methods for creating and updating the FPL team

    Attributes:
        fpl: Calls the FPLstats class for using player stats and calculating points
        team: List of the players of the team
        team_positions: List of the team's players' positions
        player_teams: List of the team's players' Premier League team
        managers: List of possible managers
        points_sum: Float of the total points calculated for the team based on the program's formula
        player_points: List of the individual players' calculated points
        captain_points: List of the individual player's calculated points for captaincy
        manager_points: List of the individual manager's calculated points
        total_budget: Float of the total budget available
        starters_budget: Float of the budget used for the team's starting players
        changes_budget: Float of the budget used for the team's changes
        bank_budget: Float of the budget left in the bank
        starters_prices: List of starting players' prices
        changes_prices: List of changes' prices
        managers_prices: List of managers' prices
        unavailable_players_list: List of players excluded from the calculation
        system: List of number of players per position in the team
    """
    def __init__(self, username, password):
        self.fpl = FPLstats(username, password)

        self.team = []
        self.team_elements = []
        self.team_positions = []
        self.player_teams = []
        self.managers = []
        self.points_sum = 0.0
        self.player_points = []
        self.captain_points = []
        self.manager_points = []
        self.total_budget = 100.0
        self.starters_budget = 0.0
        self.changes_budget = 16.5
        self.bank_budget = 0.0
        self.starters_prices = []
        self.changes_prices = []
        self.managers_prices = []
        self.unavailable_players_list = []
        self.unavailable_players_list_elements = []
        self.system = [9999, 9999, 9999]

        self.fpl.calculate_points()

    def add_player(self, mode: str, element: str) -> None:
        """
        Adds a player's statistics to the team lists

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :param element: Player ID
        :type element: str
        :return: None
        """
        calculation_mode = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
        self.team_positions.append(self.fpl.player_stat(element, "position"))
        self.team.append(self.fpl.player_stat(element, "name"))
        self.points_sum += self.fpl.player_stat(element, calculation_mode)
        self.player_teams.append(self.fpl.player_stat(element, "team"))
        self.starters_budget += round(self.fpl.player_stat(element, "cost"), 1)
        self.bank_budget -= round(self.fpl.player_stat(element, "cost"), 1)
        self.player_points.append(self.fpl.player_stat(element, calculation_mode))
        self.captain_points.append(self.fpl.player_stat(element, "captain_points"))
        self.team_elements.append(element)

    def remove_player(self, mode: str, element: str) -> None:
        """
        Removes a player's statistics from the lists

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :param element: Player ID
        :type element: str
        :return: None
        """
        calculation_mode = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
        self.team_positions.pop(self.team.index(self.fpl.player_stat(element, "name")))
        self.points_sum -= self.fpl.player_stat(element, calculation_mode)
        self.player_teams.pop(self.team.index(self.fpl.player_stat(element, "name")))
        self.starters_budget -= round(self.fpl.player_stat(element, "cost"), 1)
        self.bank_budget += round(self.fpl.player_stat(element, "cost"), 1)
        self.player_points.pop(self.team.index(self.fpl.player_stat(element, "name")))
        self.captain_points.pop(self.team.index(self.fpl.player_stat(element, "name")))
        self.team.remove(self.fpl.player_stat(element, "name"))
        self.team_elements.remove(element)

    def reset_info(self) -> None:
        """
        Resets the starting values of the team class

        :return: None
        """
        self.team = []
        self.team_elements = []
        self.team_positions = []
        self.player_teams = []
        self.managers = []
        self.points_sum = 0.0
        self.player_points = []
        self.captain_points = []
        self.manager_points = []
        self.total_budget = 100.0
        self.starters_budget = 0.0
        self.changes_budget = 16.5
        self.bank_budget = 0.0
        self.starters_prices = []
        self.changes_prices = []
        self.managers_prices = []
        self.unavailable_players_list = []
        self.unavailable_players_list_elements = []
        self.system = [9999, 9999, 9999]

    def print_result(self) -> None:
        """
        Prints the results of a calculation in a preferred format

        :return: None
        """
        print(f"\nIn the bank: {round(self.bank_budget, 1)}")
        print(f"Squad transfer value: {round(self.starters_budget, 1)}")
        print(f"Squad: {self.team}")
        print(f"Potential captains: 1) {self.team[self.captain_points.index(max(self.captain_points))]}"
              f"\t2) {self.team[self.captain_points.index(sorted(self.captain_points)[-2])]}")
        self.manager_pick()
        print(f"Potential manager: {self.managers[self.manager_points.index(max(self.manager_points))]}")
        print(f"Manager price: {self.managers_prices[self.manager_points.index(max(self.manager_points))]}")
        print(f"Total points: {self.points_sum}")
        print(f"Each player's points: {self.player_points}")
        print(f"Captaincy points: {self.captain_points}")
        print(f"Manager points: {self.manager_points[self.manager_points.index(max(self.manager_points))]}")

    def create_new_team(self, username, password) -> None:
        """
        Calculates a new team without any inputs

        :return: None
        """
        self.reset_info()
        self.user_budget_changes(username, password)
        self.bank_budget = self.total_budget - self.changes_budget
        bank_money = self.bank_budget
        total_money = self.total_budget
        changes_money = self.changes_budget
        self.reset_info()
        self.choose_system()
        self.bank_budget = bank_money
        self.total_budget = total_money
        self.changes_budget = changes_money

        self.create_loop_players(mode="normal")
        self.update_team(mode="normal")
        for element in self.team_elements:
            self.starters_prices.append(self.fpl.player_stat(element, "cost"))

    def free_hit(self, username, password) -> None:
        """
        Calculates a Free Hit team

        :return: None
        """
        self.reset_info()
        self.user_budget_changes(username, password)
        bank_money = self.total_budget - 16.5
        total_budget = self.total_budget
        self.reset_info()
        self.choose_system()
        self.bank_budget = bank_money
        self.total_budget = total_budget

        self.create_loop_players(mode="free_hit")
        self.update_team(mode="free_hit")

    def enter_new_team(self) -> None:
        """
        Accepts player names and prices in order to create a new team

        :return: None
        """
        self.reset_info()
        self.choose_system()
        budget_choice = enter_budget_choice()

        print("\nPlease enter your team (or type 'cancel' to go back).")
        while len(self.team) < 11:
            team_player = enter_player()
            player_price = enter_budget(budget_choice)
            self.enter_loop_players(team_player, budget_choice, player_price)
        self.enter_budget_changes(budget_choice)

    def open_saved_team(self) -> None:
        """
        Opens a previously saved team

        :return: None
        """
        self.reset_info()

        username = saved_get_username()
        password = saved_get_password(username)
        with open("saved_teams.json", "r") as data:
            saved_team = json.load(data)
        if password == saved_team[username]["Password"]:
            self.saved_loop_players(saved_team, username)
            self.saved_budget_changes(saved_team, username)

    def open_user_team(self, username, password) -> None:
        """
        Opens a new team based on a user's official Fantasy Premier League log-in information

        :return: None
        """
        self.reset_info()

        self.user_team_players(username, password)
        self.user_budget_changes(username, password)

    def compare_players(self) -> None:
        """
        Used for comparing players based on their captaincy points (cost value is not included)

        :return: None
        """
        print("\nThe program will create a list of players that are going to be ranked in the end based on "
              "\ncaptaincy points (meaning that their cost value is not included)."
              "\nPlease type 'stop' when you are done entering player names.\n")
        comparing_players_dict = {}
        add_player = ""
        points_list = []
        while add_player != "stop":
            add_player = input("Give a player's name: ")
            invalid = True
            if add_player == "stop":
                break
            for code in self.fpl.player_data["code"]:
                player = (
                    self.fpl.player_data["name"]
                    [self.fpl.player_data.index[self.fpl.player_data["code"] == code].tolist()[0]]
                )
                if unidecode(player.lower()) == unidecode(add_player.lower()):
                    comparing_players_dict.update({code: {player: (
                        self.fpl.player_data["captain_points"]
                        [self.fpl.player_data.index[self.fpl.player_data["code"] == code].tolist()[0]]
                    )}})
                    invalid = False
            if invalid:
                print("\nInvalid player name.")
        dict_list = list(comparing_players_dict.values())
        for player_dict in dict_list:
            points_list.append(list(player_dict.values())[0])
        points_list.sort(reverse=True)
        sorted_comparing_players_dict = {}
        for number in points_list:
            for code in comparing_players_dict:
                for name, points in comparing_players_dict[code].items():
                    if number == points:
                        sorted_comparing_players_dict.update({code: {name: points}})
        if len(comparing_players_dict) == 0:
            print("")
        else:
            print("\n   Name\t\t\tCaptaincy Points")
            for code in sorted_comparing_players_dict.keys():
                for player in sorted_comparing_players_dict[code].keys():
                    print(f"{points_list.index(sorted_comparing_players_dict[code][player]) + 1}. {player:21}"
                          f"{round(sorted_comparing_players_dict[code][player], 2)}")

    def change_players(self, mode: str) -> None:
        """
        Function for replacing players if excluded

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        # Values that are going to be checked from the team
        changing_players_elements = []
        final_changing_players_elements = []
        temp_teams = [team for team in self.player_teams]
        temp_teams_change = []
        max_budget = []
        used_players_elements = []

        player_budget = self.bank_budget
        for element in self.team_elements:
            if element in self.unavailable_players_list_elements:
                changing_players_elements.append(element)
                final_changing_players_elements.append(element)
                temp_teams_change.append(self.fpl.player_stat(element, "team"))
                player_budget += self.fpl.player_stat(element, "cost")
        max_budget.append(round(player_budget, 1))

        # Main process
        all_teams = self.pl_all_teams()
        for n in range(11):
            # Loop again and retry used players
            self.retry_players(all_teams, used_players_elements)
            for i in range(11):
                # Loop again and retry all players
                # (basically try the players that might have been suitable before the change by looping again)
                for player_element in changing_players_elements:
                    if player_element in self.team_elements or player_element in used_players_elements:
                        # First check replacing players without checking points just to remove them
                        self.change_players_first_loop(
                            used_players_elements, changing_players_elements, player_element, max_budget,
                            temp_teams, temp_teams_change, mode=mode
                        )
                    else:
                        self.change_players_more_loops(
                            used_players_elements, changing_players_elements, player_element, max_budget,
                            temp_teams, temp_teams_change, mode=mode
                        )
        for player_element in changing_players_elements:
            self.add_player(mode="normal", element=player_element)
        for element in final_changing_players_elements:
            self.remove_player(mode="normal", element=element)
        self.print_result()

    def update_team(self, mode: str) -> None:
        """
        Updates the entire FPL team

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        all_teams = self.pl_all_teams()

        used_players_elements = []
        max_budget = round(self.total_budget - self.changes_budget, 1)

        for n in range(11):
            # Loop again and retry used players
            self.retry_players(all_teams, used_players_elements)
            for i in range(11):
                # Loop again and retry all players
                # (basically try the players that might have been suitable before the change by looping again)
                for player_element in self.team_elements:
                    if (
                        player_element in self.unavailable_players_list_elements
                        or player_element in used_players_elements
                    ):
                        # First check replacing players without checking points just to remove them
                        self.update_team_first_loop(used_players_elements, player_element, max_budget, mode)
                    else:
                        self.update_team_more_loops(used_players_elements, player_element, max_budget, mode)
        self.print_result()

    def transfer_players(self, mode: str) -> None:
        """
        Used for transferring players and hold information on player availability

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        continue_updating = ""
        while continue_updating.lower() != "skip":
            continue_updating = input("\nDo you want to exclude any players or get suggestion "
                                      "(exclude/suggestion/skip/cancel)? ")
            if continue_updating.lower() == "exclude":
                break
            elif continue_updating.lower() == "skip":
                return None
            elif continue_updating.lower() == "cancel":
                raise ValueError
            elif continue_updating.lower() == "suggestion":
                self.transfer_calculation(mode=mode)
            else:
                print("\nInvalid answer.")

        unavailable_player = ""
        invalid_check = []
        while (
                unavailable_player.lower() != "stop"
                and unavailable_player.lower() != "none"
                and unavailable_player.lower() != "all"
                and unavailable_player.lower() != "update"
                and unavailable_player.lower() != "suggestion"
                and unavailable_player.lower() != "cancel"
        ):
            invalid_check.clear()
            unavailable_player = input("\nAdd players to the exclusion list "
                                       "(player/suggestion/all/none/update/stop/cancel): ")
            if unavailable_player.lower() == "stop":
                break
            if unavailable_player.lower() == "none":
                self.unavailable_players_list = []
                break
            if unavailable_player.lower() == "cancel":
                raise ValueError
            for pl_element in self.team_elements:
                if unavailable_player.lower() == "all" and pl_element not in self.unavailable_players_list_elements:
                    self.unavailable_players_list_elements.append(pl_element)
            if unavailable_player.lower() == "update":
                self.update_team(mode=mode)
                self.transfer_players(mode=mode)
                return None
            if unavailable_player.lower() == "suggestion":
                self.transfer_calculation(mode=mode)
                self.transfer_players(mode=mode)
                return None
            for element in self.fpl.player_data["id_x"]:
                if unidecode(unavailable_player.lower()) == unidecode(self.fpl.player_stat(element, "name").lower()):
                    if element not in self.unavailable_players_list_elements:
                        self.unavailable_players_list_elements.append(element)
                        break
                    else:
                        print("\nThe player is already excluded.")
            for element in self.fpl.player_data["id_x"]:
                if (
                    unidecode(unavailable_player.lower()) != unidecode(self.fpl.player_stat(element, "name").lower())
                    and unavailable_player.lower() != "all"
                    and unavailable_player.lower() != "update"
                    and unavailable_player.lower() != "suggestion"
                ):
                    invalid_check.append(1)
                else:
                    invalid_check.append(0)
            if 0 not in invalid_check:
                print("\nInvalid answer.")
            for element in self.unavailable_players_list_elements:
                if self.fpl.player_stat(element, "name") not in self.unavailable_players_list:
                    self.unavailable_players_list.append(self.fpl.player_stat(element, "name"))
            print(f"Excluded players: {self.unavailable_players_list}")

        # Replacement part
        continue_replacement = False
        if len(self.unavailable_players_list) > 0:
            player_not_in_team = []
            for player in self.unavailable_players_list:
                if player in self.team:
                    continue_replacement = True
                else:
                    player_not_in_team.append(1)
            if continue_replacement:
                if unavailable_player.lower() == "all":
                    self.update_team(mode=mode)
                    self.transfer_players(mode=mode)
                    return None
                elif unavailable_player.lower() == "stop":
                    changes_choice = ""
                    while (
                           changes_choice.lower() != "replace"
                           and changes_choice.lower() != "update"
                           and changes_choice.lower() != "cancel"
                    ):
                        input_text = ""
                        input_text_2 = ""
                        if mode == "normal":
                            input_text = "replace/wonderpick/"
                            input_text_2 = ", wonder pick for one GW"
                        elif mode == "free_hit":
                            input_text = ""
                        changes_choice = input(f"\nDo you want to find replacements{input_text_2}"
                                               f" or update the entire team ({input_text}update/cancel)? ")
                        if changes_choice.lower() == "replace":
                            if mode == "normal":
                                self.change_players(mode=mode)
                                self.transfer_players(mode=mode)
                                return None
                            elif mode == "free_hit":
                                self.update_team(mode=mode)
                                self.transfer_players(mode=mode)
                                return None
                        elif changes_choice.lower() == "update":
                            self.update_team(mode=mode)
                            self.transfer_players(mode=mode)
                            return None
                        elif changes_choice.lower() == "wonderpick":
                            if mode == "normal":
                                self.change_players(mode="free_hit")
                                self.transfer_players(mode=mode)
                                return None
                            elif mode == "free_hit":
                                self.update_team(mode=mode)
                                self.transfer_players(mode=mode)
                                return None
                        elif changes_choice.lower() == "cancel":
                            raise ValueError
                        else:
                            print("\nInvalid answer.")
            elif 1 in player_not_in_team:
                self.transfer_players(mode=mode)
                return None

    def transfer_calculation(self, mode: str) -> None:
        """
        Calculates whether an extra player transfer is worth the -4 points and gives a list of suggestions

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        # Calculation for single transfer
        if mode == "normal":
            self.transfer_single_loop()
        elif mode == "free_hit":
            print("\nThere is no point running the single player changes suggestion since the Free Hit choice "
                  "gives the optimal team.")

        extended_suggestion = ""
        while (
               extended_suggestion.lower() != "yes"
               and extended_suggestion.lower() != "no"
               and extended_suggestion.lower() != "cancel"
        ):
            extended_suggestion = input("\nWould you like to run the extended suggestion "
                                        "for double player changes (yes/no/cancel)? ")
            if (
                extended_suggestion.lower() != "yes"
                and extended_suggestion.lower() != "no"
                and extended_suggestion.lower() != "cancel"
            ):
                print("\nInvalid answer.")
            if extended_suggestion.lower() == "yes":
                # Calculation for double transfer
                self.transfer_double_loop(mode=mode)
            if extended_suggestion.lower() == "cancel":
                raise ValueError

    def choose_system(self) -> None:
        """
        Holds information on the team's system

        :return: None
        """
        print("\nPlease enter the system for your squad.")
        self.system[0] = 9999
        self.system[1] = 9999
        self.system[2] = 9999
        while (
            5 < self.system[0] or self.system[0] < 3
            or 5 < self.system[1] or self.system[1] < 1
            or 3 < self.system[2] or self.system[2] < 1
            or 10 != self.system[0] + self.system[1] + self.system[2]
        ):
            for number in self.system:
                self.system.pop(self.system.index(number))
                self.system.append(9999)
            try:
                system_def = input("\nDEF: ")
                if system_def == "cancel":
                    raise ReferenceError
                self.system[0] = int(system_def)
                system_mid = input("MID: ")
                if system_mid == "cancel":
                    raise ReferenceError
                self.system[1] = int(system_mid)
                system_fwd = input("FWD: ")
                if system_fwd == "cancel":
                    raise ReferenceError
                self.system[2] = int(system_fwd)
            except ValueError:
                print("")
            except ReferenceError:
                raise ValueError
            if (
                5 < self.system[0] or self.system[0] < 3
                or 5 < self.system[1] or self.system[1] < 1
                or 3 < self.system[2] or self.system[2] < 1
                or 10 != self.system[0] + self.system[1] + self.system[2]
            ):
                print("\nInvalid system.")

    def save_team(self) -> None:
        """
        Saves the team for future use

        :return: None
        """
        choice = ""
        while choice.lower() != "yes" and choice.lower() != "no":
            choice = input("\nDo you want to save your team for the future (yes/no)? ")
            if choice.lower() == "yes":
                new_user = ""
                while (
                    new_user.lower() != "yes"
                    and new_user.lower() != "no"
                    and new_user.lower() != "cancel"
                ):
                    new_user = input("\nDo you want to create a new user entry (yes/no/cancel)? ")
                    if new_user.lower() == "yes":
                        self.save_new_entry()
                    elif new_user.lower() == "no":
                        try:
                            with open("saved_teams.json", "r") as data:
                                saved_teams = json.load(data)
                        except FileNotFoundError:
                            print("\nThere are no previously saved teams.")
                            new_user = ""
                            continue
                        new_user = self.save_old_entry(new_user, saved_teams)
                    elif new_user.lower() == "cancel":
                        return None
                    else:
                        print("\nInvalid answer.")
            elif choice == "no":
                return None
            else:
                print("\nInvalid answer.")

    def create_loop_players(self, mode: str) -> None:
        """
        Loops through the player database to create a team

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        for element in self.fpl.player_data["id_x"]:
            if (
                # Check team limit
                self.player_teams.count(self.fpl.player_stat(element, "team")) > 2
                # Check managers out
                or self.fpl.player_stat(element, "position") == "MNG"
                # Check position limit
                or (self.fpl.player_stat(element, "position") == "GKP"
                    and self.team_positions.count("GKP") == 1)
                or (self.fpl.player_stat(element, "position") == "DEF"
                    and self.team_positions.count("DEF") == self.system[0])
                or (self.fpl.player_stat(element, "position") == "MID"
                    and self.team_positions.count("MID") == self.system[1])
                or (self.fpl.player_stat(element, "position") == "FWD"
                    and self.team_positions.count("FWD") == self.system[2])
            ):
                continue
            else:
                self.add_player(mode=mode, element=element)

    def enter_loop_players(self, team_player: str, budget_choice: str, player_price: float) -> None:
        """
        Loops through the player database in search of the player name given and add him to the team
        (used in the enter_new_team method)

        :param team_player: Name of the player the method searches for
        :type team_player: str
        :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no')
        :type budget_choice: str
        :param player_price: Price of the player the method searches for
        :type player_price: float
        :return: None
        """
        invalid = False
        for element in self.fpl.player_data["id_x"]:
            player = (
                self.fpl.player_data["name"]
                [self.fpl.player_data.index[self.fpl.player_data["id_x"] == element].tolist()[0]]
            )
            if (
                # Check if the player exists
                unidecode(player.lower()) == unidecode(team_player.lower())
                # Check if the player is already in the team
                and player not in self.team
                # Check team limit
                and self.player_teams.count(self.fpl.player_stat(element, "team")) < 3
                # Check position limit
                and (
                     self.fpl.player_stat(element, "position") == "GKP"
                     and self.team_positions.count("GKP") < 1
                     or self.fpl.player_stat(element, "position") == "DEF"
                     and self.team_positions.count("DEF") < self.system[0]
                     or self.fpl.player_stat(element, "position") == "MID"
                     and self.team_positions.count("MID") < self.system[1]
                     or self.fpl.player_stat(element, "position") == "FWD"
                     and self.team_positions.count("FWD") < self.system[2]
                )
            ):
                # Changing the player cost in the main_df based on the selling price we get
                # from the input
                # The functionality of changing the main_df here is based on the fact that the
                # info of the main_df is stored in the cache and the fpl_player_stats function
                # just calls the result from there without running again
                # (a bit of cheating someone might say... *sips tea sardonically*)
                if budget_choice.lower() == "yes":
                    self.fpl.fplapi.main_df.loc[self.fpl.fplapi.main_df.index[
                        self.fpl.fplapi.main_df["id_x"] == element], ["cost"]
                    ] = player_price
                    self.starters_prices.append(player_price)
                self.add_player(mode="normal", element=element)
                invalid = False
                break
            else:
                invalid = True
        if invalid:
            print("\nInvalid player name.")

    def enter_budget_changes(self, budget_choice: str) -> None:
        """
        Changes the budget values if used (in the enter_new_team method)

        :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no')
        :type budget_choice: str
        :return: None
        """
        if budget_choice.lower() == "no":
            self.bank_budget += 100.0 - 16.5

        if budget_choice.lower() == "yes":
            self.starters_budget = round(sum(self.starters_prices), 1)

        changes_budget = ""
        type_error = True
        cancel_value_changes = False
        if budget_choice.lower() == "yes":
            while type_error:
                try:
                    changes_budget_str = input("Enter your changes' budget: ")
                    if changes_budget_str.lower() == "cancel":
                        cancel_value_changes = True
                        break
                    changes_budget = float(changes_budget_str)
                    type_error = False
                except ValueError:
                    print("\nInvalid budget.")
            if cancel_value_changes:
                raise ValueError
            self.changes_budget = changes_budget

        bank_budget = ""
        type_error = True
        cancel_value_bank = False
        if budget_choice.lower() == "yes":
            while type_error:
                try:
                    bank_budget_str = input("Enter your budget in the bank: ")
                    if bank_budget_str.lower() == "cancel":
                        cancel_value_bank = True
                        break
                    bank_budget = float(bank_budget_str)
                    type_error = False
                except ValueError:
                    print("\nInvalid budget.")
            if cancel_value_bank:
                raise ValueError
            self.bank_budget = bank_budget

        if budget_choice.lower() == "yes":
            self.total_budget = round(self.starters_budget + self.changes_budget + self.bank_budget, 1)

    def saved_loop_players(self, saved_team: dict, username: str) -> None:
        """
        Loops through the player database in search of the players in the saved team file and updates the team
        (used in the open_saved_team method)

        :param saved_team: Dictionary of the saved team taken from the .json file
        :type saved_team: dict
        :param username: The user's username
        :type username: str
        :return:
        """
        # Changing the player cost in the main_df based on the selling price we get
        # from the saved_team
        # The functionality of changing the main_df here is based on the fact that the
        # info of the main_df is stored in the cache and the fpl_player_stats function
        # just calls the result from there without running again
        # (a bit of cheating someone might say... *sips tea sardonically*)
        for element in saved_team[username]["Team_elements"]:
            self.fpl.fplapi.main_df.loc[self.fpl.fplapi.main_df.index[
                self.fpl.fplapi.main_df["id_x"] == element], ["cost"]] = saved_team[username]["Starters_prices"][
                saved_team[username]["Team_elements"].index(element)]
        for element in saved_team[username]["Team_elements"]:
            self.add_player(mode="normal", element=element)

    def saved_budget_changes(self, saved_team: dict, username: str) -> None:
        """
        Changes the budget values in the open_saved_team method

        :param saved_team: Dictionary of the saved team taken from the .json file
        :type saved_team: dict
        :param username: The user's username
        :type username: str
        :return: None
        """
        self.total_budget = round(saved_team[username]["Total_budget"], 1)
        self.starters_budget = round(saved_team[username]["Starters_budget"], 1)
        self.changes_budget = round(saved_team[username]["Changes_budget"], 1)
        self.bank_budget = round(saved_team[username]["Bank_budget"], 1)
        self.starters_prices = saved_team[username]["Starters_prices"]
        self.changes_prices = saved_team[username]["Changes_prices"]

    def user_team_players(self, username, password) -> None:
        """
        Gets the user's team from the official FPL API using his log-in information
        (used in the open_user_team method)

        :return: None
        """
        team_list_elements = self.fpl.fplapi.get_team(username, password)["team_elements"]
        team_starters_ids = []
        for number in range(11):
            team_starters_ids.append(team_list_elements[number])
        for element in team_starters_ids:
            self.add_player(mode="normal", element=element)

    def user_budget_changes(self, username, password) -> None:
        """
        Changes the budget values in the open_user_team method

        :return: None
        """
        self.total_budget = round(self.fpl.fplapi.get_team(username, password)["total_budget"], 1)
        self.starters_budget = round(self.fpl.fplapi.get_team(username, password)["starters_budget"], 1)
        self.changes_budget = round(self.fpl.fplapi.get_team(username, password)["changes_budget"], 1)
        self.bank_budget = round(self.fpl.fplapi.get_team(username, password)["bank_budget"], 1)
        self.starters_prices = self.fpl.fplapi.get_team(username, password)["starters_prices"]
        self.changes_prices = self.fpl.fplapi.get_team(username, password)["changes_prices"]

    def pl_all_teams(self) -> list:
        """
        Creates a list of all the premier league teams

        :return: A list of all the premier league teams
        """
        all_teams = []
        for team in self.fpl.player_data["team"]:
            if team not in all_teams:
                all_teams.append(team)
        return all_teams

    def retry_players(self, all_teams: list, used_players_elements: list) -> None:
        """
        Makes the player available for the team again if his premier league team doesn't appear more than 2 times in
        the players' teams count according to the FPL rules

        :param all_teams: A list of all the premier league teams
        :type all_teams: list
        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :return: None
        """
        for team in all_teams:
            if self.player_teams.count(team) < 3:
                for n in range(11):
                    for element in used_players_elements:
                        if self.fpl.player_stat(element, "team") == team:
                            used_players_elements.remove(element)

    def change_players_first_loop(
            self, used_players_elements: list, changing_players_elements: list, player_element: str, max_budget: list,
            temp_teams: list, temp_teams_change: list, mode: str
    ) -> None:
        """
        First loop through players in the change_players method (Just replacing the original changing players)

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param changing_players_elements: A list of the player IDs in the process of changing
        :type changing_players_elements: list
        :param player_element: A player ID from the changing_players_elements list
        :type player_element: str
        :param max_budget: A list containing the maximum budget for the player change
        :type max_budget: list
        :param temp_teams: A list of the team's players' premier league teams
        :type temp_teams: list
        :param temp_teams_change: A list of the changing players' premier league teams
        :type temp_teams_change: list
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
        for element in self.fpl.player_data["id_x"]:
            if (
                self.player_checks(element, player_element, used_players_elements)
                # Check if the player is already in the players that are about to change
                and element not in changing_players_elements
                # Check for valid points
                and self.fpl.player_stat(element, calculation_mode) > 0
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(element, "cost")
                     + sum([self.fpl.player_stat(element, "cost") for element in changing_players_elements
                            if element != player_element])
                    ), 1
                )
                if temporary_budget <= max_budget[0]:
                    # Checking the budget limit
                    player_team_number = (temp_teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == temp_teams_change[changing_players_elements.index(player_element)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            update_list(changing_players_elements, element, player_element)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )
                            break
                    else:
                        if player_team_number < 3:
                            update_list(changing_players_elements, element, player_element)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )
                            break

    def change_players_more_loops(
            self, used_players_elements: list, changing_players_elements: list, player_element: str, max_budget: list,
            temp_teams: list, temp_teams_change: list, mode: str
    ) -> None:
        """
        Loops after the first loop through players in the change_players method

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param changing_players_elements: A list of the player IDs in the process of changing
        :type changing_players_elements: list
        :param player_element: A player ID from the changing_players_elements list
        :type player_element: str
        :param max_budget: A list containing the maximum budget for the player change
        :type max_budget: list
        :param temp_teams: A list of the team's players' premier league teams
        :type temp_teams: list
        :param temp_teams_change: A list of the changing players' premier league teams
        :type temp_teams_change: list
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
        for element in self.fpl.player_data["id_x"]:
            if (
                self.player_checks(element, player_element, used_players_elements)
                # Check if the player is already in the players that are about to change
                and element not in changing_players_elements
                # Check for valid points
                and self.fpl.player_stat(element, calculation_mode) > 0
                # Check for better points
                and sum([self.fpl.player_stat(pl_element, calculation_mode)
                         for pl_element in changing_players_elements])
                < self.fpl.player_stat(element, calculation_mode)
                + sum([self.fpl.player_stat(pl_element, calculation_mode)
                       for pl_element in changing_players_elements if pl_element != player_element])
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(element, "cost")
                     + sum([self.fpl.player_stat(pl_element, "cost") for pl_element in changing_players_elements
                            if pl_element != player_element])
                    ), 1
                )
                if temporary_budget <= max_budget[0]:
                    # Checking the budget limit
                    player_team_number = (temp_teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == (temp_teams_change[changing_players_elements.index(player_element)])
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            update_list(changing_players_elements, element, player_element)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )
                            break
                    else:
                        if self.fpl.player_stat(element, "team") in temp_teams_change:
                            # Check for players on the team limit in order to pick the best ones in the
                            # next loop
                            for pl_element in changing_players_elements:
                                if (
                                    # Checking for players other than the player that's currently
                                    # updating
                                    pl_element != player_element
                                    # Check for better points
                                    and self.fpl.player_stat(pl_element, calculation_mode)
                                    > self.fpl.player_stat(element, calculation_mode) > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Check team
                                    and (
                                         self.fpl.player_stat(pl_element, "team")
                                         == self.fpl.player_stat(element, "team")
                                    )
                                    # Don't enter the name twice in the list
                                    and element not in used_players_elements
                                ):
                                    used_players_elements.append(element)
                                elif (
                                      # Checking for players other than the player that's currently
                                      # updating
                                      pl_element != player_element
                                      # Check for better points
                                      and 0 < self.fpl.player_stat(pl_element, calculation_mode)
                                      < self.fpl.player_stat(element, calculation_mode)
                                      # Check team limit
                                      and player_team_number > 2
                                      # Check team
                                      and (
                                           self.fpl.player_stat(pl_element, "team")
                                           == self.fpl.player_stat(element, "team")
                                      )
                                      # Don't enter the name twice in the list
                                      and pl_element not in used_players_elements
                                ):
                                    used_players_elements.append(pl_element)
                        if player_team_number < 3:
                            update_list(changing_players_elements, element, player_element)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(element, "team"),
                                self.fpl.player_stat(player_element, "team")
                            )
                            break

    def update_team_first_loop(self, used_players_elements: list, player_element: str,
                               max_budget: float, mode: str) -> None:
        """
        First loop through players in the update_team method (Just replacing the original players)

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param player_element: A player ID from the team list
        :type player_element: str
        :param max_budget: A float of the maximum budget for the team
        :type max_budget: float
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        for element in self.fpl.player_data["id_x"]:
            if self.player_checks(element, player_element, used_players_elements):
                temporary_budget = round(
                    (
                     self.starters_budget
                     + self.fpl.player_stat(element, "cost")
                     - self.fpl.player_stat(player_element, "cost")
                    ), 1
                )
                if temporary_budget <= max_budget:
                    # Checking the budget limit
                    player_team_number = (self.player_teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == self.player_teams[self.team_elements.index(player_element)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            self.add_player(mode=mode, element=element)
                            self.remove_player(mode=mode, element=player_element)
                            break
                    else:
                        if player_team_number < 3:
                            self.add_player(mode=mode, element=element)
                            self.remove_player(mode=mode, element=player_element)
                            break

    def update_team_more_loops(self, used_players_elements: list, player_element: str,
                               max_budget: float, mode: str) -> None:
        """
        Loops after the first loop through players in the update_team method

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param player_element: A player ID from the team list
        :type player_element: str
        :param max_budget: A float of the maximum budget for the team
        :type max_budget: float
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
        for element in self.fpl.player_data["id_x"]:
            if (
                self.player_checks(element, player_element, used_players_elements)
                # Check for better points
                and self.fpl.player_stat(element, calculation_mode)
                > self.fpl.player_stat(player_element, calculation_mode)
            ):
                temporary_budget = round(
                    (
                     self.starters_budget
                     + self.fpl.player_stat(element, "cost")
                     - self.fpl.player_stat(player_element, "cost")
                    ), 1
                )
                if temporary_budget <= max_budget:
                    # Checking the budget limit
                    player_team_number = (self.player_teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == self.player_teams[self.team_elements.index(player_element)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            self.add_player(mode=mode, element=element)
                            self.remove_player(mode=mode, element=player_element)
                            break
                    else:
                        if self.fpl.player_stat(element, "team") in self.player_teams:
                            # Check for players on the team limit in order to pick the best ones in the
                            # next loop
                            for pl_element in self.team_elements:
                                if (
                                    # Checking for players other than the player that's currently
                                    # updating
                                    pl_element != player_element
                                    # Check for better points
                                    and self.fpl.player_stat(pl_element, calculation_mode)
                                    > self.fpl.player_stat(element, calculation_mode) > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Check team
                                    and self.fpl.player_stat(pl_element, "team")
                                    == self.fpl.player_stat(element, "team")
                                    # Don't enter the name twice in the list
                                    and element not in used_players_elements
                                ):
                                    used_players_elements.append(element)
                                elif (
                                      # Checking for players other than the player that's currently
                                      # updating
                                      pl_element != player_element
                                      # Check for better points
                                      and 0 < self.fpl.player_stat(pl_element, calculation_mode)
                                      < self.fpl.player_stat(element, calculation_mode)
                                      # Check team limit
                                      and player_team_number > 2
                                      # Check team
                                      and (
                                           self.fpl.player_stat(pl_element, "team")
                                           == self.fpl.player_stat(element, "team")
                                      )
                                      # Don't enter the name twice in the list
                                      and pl_element not in used_players_elements
                                ):
                                    used_players_elements.append(pl_element)
                        if player_team_number < 3:
                            self.add_player(mode=mode, element=element)
                            self.remove_player(mode=mode, element=player_element)
                            break

    def transfer_single_loop(self) -> None:
        """
        Single transfer suggestion loop

        :return: None
        """
        max_budget_single_transfer = round(self.total_budget - self.changes_budget, 1)
        used_players_elements = []
        for pl_element in self.team_elements:
            possible_transfers = {}
            for element in self.fpl.player_data["id_x"]:
                if (
                    self.player_checks(element, pl_element, used_players_elements)
                    # Check for better transfer points
                    and (
                         self.fpl.player_stat(element, "transfer_points")
                         >= self.player_points[self.team_elements.index(pl_element)]
                    )
                ):
                    temporary_budget = round(
                        (
                         self.starters_budget
                         + self.fpl.player_stat(element, "cost")
                         - self.fpl.player_stat(pl_element, "cost")
                        ), 1
                    )
                    if temporary_budget <= max_budget_single_transfer:
                        # Checking the budget limit
                        player_team_number = (
                            self.player_teams.count(self.fpl.player_stat(element, "team"))
                        )
                        if (
                            self.fpl.player_stat(element, "team")
                            == self.player_teams[self.team_elements.index(pl_element)]
                        ):
                            # Check team limit
                            if player_team_number < 4:
                                transfer_per_dif = round(
                                    (self.fpl.player_stat(element, "transfer_points")
                                     / (self.fpl.player_stat(element, "transfer_points")
                                        + self.fpl.player_stat(pl_element, "point_calculation"))) * 100, 2
                                )
                                possible_transfers.update({self.fpl.player_stat(element, "name"): transfer_per_dif})
                        else:
                            if player_team_number < 3:
                                transfer_per_dif = round(
                                    (self.fpl.player_stat(element, "transfer_points")
                                     / (self.fpl.player_stat(element, "transfer_points")
                                        + self.fpl.player_stat(pl_element, "point_calculation"))) * 100, 2
                                )
                                possible_transfers.update({self.fpl.player_stat(element, "name"): transfer_per_dif})
            percentage_list = list(possible_transfers.values())
            percentage_list.sort(reverse=True)
            sorted_possible_transfers = {}
            for number in percentage_list:
                for name, percentage in possible_transfers.items():
                    if number == percentage:
                        sorted_possible_transfers.update({name: percentage})
            print(f"\nPossible transfers for {self.fpl.player_stat(pl_element, 'name')}: ")
            if len(possible_transfers) == 0:
                print("-")
            else:
                print("Name\t\t\tBetter Value Possibility")
                for name in sorted_possible_transfers:
                    print(f"{name:<24}{sorted_possible_transfers[name]} %")

    def transfer_double_first_loop(self, used_players_elements: list, possible_transfers_elements: dict, key: int,
                                   player_element: str,
                                   max_budget: list, teams: list, teams_transfer: list, mode: str) -> None:
        """
        Double transfer suggestion first loop through players
        (Just replacing the original players of the possible transfer)

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param possible_transfers_elements: A dictionary of the possible double transfer combinations
        :type possible_transfers_elements: dict
        :param key: The key of the possible_transfers dictionary
        :type key: int
        :param player_element: A player ID from the team list
        :type player_element: str
        :param max_budget: A list of the possible max budgets
        :type max_budget: list
        :param teams: A list of the premier league teams of the players in the team, which updates while transfer
        calculations are taking place
        :type teams: list
        :param teams_transfer: A list of the premier league teams of the players in the possible_transfers dictionary
        :type teams_transfer: list
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode_transfer = ""
        if mode == "normal":
            calculation_mode_transfer = "transfer_points"
        elif mode == "free_hit":
            calculation_mode_transfer = "captain_points"
        for element in self.fpl.player_data["id_x"]:
            if (
                self.player_checks(element, player_element, used_players_elements)
                # Check if the name is already in the changing duo
                and element not in possible_transfers_elements[key]
                # Check for valid transfer points
                and self.fpl.player_stat(element, calculation_mode_transfer) > 0
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(element, "cost")
                     + sum([self.fpl.player_stat(pl_element, "cost")
                            for pl_element in possible_transfers_elements[key]
                            if pl_element != player_element])
                    ), 1
                )
                if temporary_budget <= max_budget[key]:
                    # Checking the budget limit
                    player_team_number = (teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == teams_transfer[0][possible_transfers_elements[key].index(player_element)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            possible_transfers_elements[key] = list(map(lambda x: element if x == player_element else x,
                                                                        possible_transfers_elements[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(element, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                player_element, "team"))

                            teams.append(self.fpl.player_stat(element, "team"))
                            teams.remove(self.fpl.player_stat(player_element, "team"))
                            break
                    else:
                        if player_team_number < 3:
                            possible_transfers_elements[key] = list(map(lambda x: element if x == player_element else x,
                                                                        possible_transfers_elements[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(element, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                player_element, "team"))

                            teams.append(self.fpl.player_stat(element, "team"))
                            teams.remove(self.fpl.player_stat(player_element, "team"))
                            break

    def transfer_double_more_loops(self, used_players_elements: list, possible_transfers_elements: dict, key: int,
                                   player_element: str,
                                   max_budget: list, teams: list, teams_transfer: list, mode: str) -> None:
        """
        Double transfer suggestion loops after the first loop through players

        :param used_players_elements: A list of the player IDs already used in the loops
        :type used_players_elements: list
        :param possible_transfers_elements: A dictionary of the possible double transfer combinations
        :type possible_transfers_elements: dict
        :param key: The key of the possible_transfers dictionary
        :type key: int
        :param player_element: A player ID from the team list
        :type player_element: str
        :param max_budget: A list of the possible max budgets
        :type max_budget: list
        :param teams: A list of the premier league teams of the players in the team, which updates while transfer
        calculations are taking place
        :type teams: list
        :param teams_transfer: A list of the premier league teams of the players in the possible_transfers dictionary
        :type teams_transfer: list
        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode_transfer = ""
        if mode == "normal":
            calculation_mode_transfer = "transfer_points"
        elif mode == "free_hit":
            calculation_mode_transfer = "captain_points"
        for element in self.fpl.player_data["id_x"]:
            if (
                self.player_checks(element, player_element, used_players_elements)
                # Check if the name is already in the changing duo
                and element not in possible_transfers_elements[key]
                # Check for valid transfer points
                and self.fpl.player_stat(element, calculation_mode_transfer) > 0
                # Check for better transfer points
                and sum([self.fpl.player_stat(pl_element, calculation_mode_transfer)
                         for pl_element in possible_transfers_elements[key]])
                < self.fpl.player_stat(element, calculation_mode_transfer)
                + [self.fpl.player_stat(pl_element, calculation_mode_transfer)
                   for pl_element in possible_transfers_elements[key] if pl_element != player_element]
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(element, "cost")
                     + sum([self.fpl.player_stat(player, "cost")
                            for player in possible_transfers_elements[key]
                            if player != player_element])
                    ), 1
                )
                if temporary_budget <= max_budget[key]:
                    # Checking the budget limit
                    player_team_number = (teams.count(self.fpl.player_stat(element, "team")))
                    if (
                        self.fpl.player_stat(element, "team")
                        == (teams_transfer[0][possible_transfers_elements[key].index(player_element)])
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            possible_transfers_elements[key] = list(map(lambda x: element if x == player_element else x,
                                                                        possible_transfers_elements[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(element, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                player_element, "team"))

                            teams.append(self.fpl.player_stat(element, "team"))
                            teams.remove(self.fpl.player_stat(
                                player_element, "team"))
                            break
                    else:
                        if self.fpl.player_stat(element, "team") in teams_transfer[0]:
                            # Check for players on the team limit in order to pick the
                            # best ones in the next loop
                            for pl_element in possible_transfers_elements[key]:
                                if (
                                    # Checking for players other than the player
                                    # that's currently updating
                                    pl_element != player_element
                                    # Check for better transfer points
                                    and self.fpl.player_stat(pl_element, calculation_mode_transfer)
                                    > self.fpl.player_stat(element, calculation_mode_transfer) > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Don't enter the name twice in the list
                                    and element not in used_players_elements
                                ):
                                    used_players_elements.append(element)
                                elif (
                                      # Checking for players other than the player
                                      # that's currently updating
                                      pl_element != player_element
                                      # Check for better transfer points
                                      and 0 < self.fpl.player_stat(pl_element, calculation_mode_transfer)
                                      < self.fpl.player_stat(element, calculation_mode_transfer)
                                      # Check team limit
                                      and player_team_number > 2
                                      # Don't enter the name twice in the list
                                      and pl_element not in used_players_elements
                                ):
                                    used_players_elements.append(pl_element)
                        if player_team_number < 3:
                            possible_transfers_elements[key] = list(map(lambda x: element if x == player_element else x,
                                                                        possible_transfers_elements[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(element, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                player_element, "team"))

                            teams.append(self.fpl.player_stat(element, "team"))
                            teams.remove(self.fpl.player_stat(
                                player_element, "team"))
                            break

    def transfer_double_loop(self, mode: str) -> None:
        """
        Double transfer suggestion loop

        :param mode: Option between 'normal' and 'free_hit' that determines the type of update
        :type mode: str
        :return: None
        """
        calculation_mode = ""
        calculation_mode_transfer = ""
        if mode == "normal":
            calculation_mode = "point_calculation"
            calculation_mode_transfer = "transfer_points"
        elif mode == "free_hit":
            calculation_mode = "captain_points"
            calculation_mode_transfer = "captain_points"
        # Combinations of 2 from the team
        possible_transfers = self.transfer_combinations()

        # Values that are going to be checked from the team
        max_budget = []
        starting_transfer_points_list = []
        for key in possible_transfers.keys():
            player_budget = self.bank_budget
            for pl_element in possible_transfers[key]:
                player_budget += self.fpl.player_stat(pl_element, "cost")
            max_budget.append(round(player_budget, 1))
            changing_player_points = [self.fpl.player_stat(pl_element, calculation_mode)
                                      for pl_element in possible_transfers[key]]
            starting_transfer_points_list.append(changing_player_points)
        all_teams = self.pl_all_teams()

        for key in possible_transfers.keys():
            # Loop on all duo combinations
            used_players_elements = []
            teams_transfer = []
            teams = [x for x in self.player_teams]
            teams_transfer.append([self.fpl.player_stat(possible_transfers[key][0], "team"),
                                   self.fpl.player_stat(possible_transfers[key][1], "team")])
            print(f"\nPossible transfers for ['{self.fpl.player_stat(possible_transfers[key][0], 'name')}', "
                  f"'{self.fpl.player_stat(possible_transfers[key][1], 'name')}']:")
            for n in range(11):
                # Loop again and retry used players
                self.retry_players(all_teams, used_players_elements)
                for i in range(11):
                    # Loop again and retry all players
                    # (basically try the players that might have been suitable before the change
                    # by looping again)
                    for player_element in possible_transfers[key]:
                        if player_element in self.team_elements or player_element in used_players_elements:
                            # First check replacing players without checking points just to remove them
                            self.transfer_double_first_loop(used_players_elements, possible_transfers, key,
                                                            player_element, max_budget, teams, teams_transfer,
                                                            mode=mode)
                        else:
                            self.transfer_double_more_loops(used_players_elements, possible_transfers, key,
                                                            player_element, max_budget, teams, teams_transfer,
                                                            mode=mode)

            final_transfer_points = [self.fpl.player_stat(pl_element, calculation_mode_transfer)
                                     for pl_element in possible_transfers[key]]
            value_possibility = round(((final_transfer_points[0] / (final_transfer_points[0]
                                                                    + starting_transfer_points_list[key][0]))
                                       + (final_transfer_points[1] / (final_transfer_points[1]
                                                                      + starting_transfer_points_list[key][1])))
                                      / 2 * 100, 2)
            if value_possibility < 50:
                print("-")
            else:
                player_string = "["
                for pl_element in possible_transfers[key]:
                    player_string += f"'{self.fpl.player_stat(pl_element, 'name')}', "
                player_string = player_string[:-2] + "]"
                print("Players\t\t\t\t\tBetter Value Possibility")
                print(f"{player_string:<40}{value_possibility} %")

    def transfer_combinations(self) -> dict:
        """
        Calculates all the possible duos from the team

        :return: A dictionary of possible double transfers from the team
        """
        possible_transfers = {}
        i = 0
        for players_elements in combinations(self.team_elements, 2):
            players_elements = list(players_elements)
            possible_transfers.update({i: players_elements})
            i += 1
        return possible_transfers

    def save_new_entry(self) -> None:
        """
        Creates a new save entry

        :return: None
        """
        try:
            with open("saved_teams.json", "r") as data:
                saved_teams = json.load(data)
        except FileNotFoundError:
            with open("saved_teams.json", "w") as data:
                json.dump({}, data, indent=4)
            with open("saved_teams.json", "r") as data_file:
                saved_teams = json.load(data_file)

        username = input("\nPlease enter your username: ")
        while username in saved_teams.keys():
            if username in saved_teams.keys():
                print("\nThis username is already taken.")
            username = input("\nPlease enter your username: ")

        password = ""
        password_check = "."
        while password_check != password:
            password = getpass("\nPlease enter your password: ")
            password_check = getpass("\nPlease confirm password: ")
            if password_check == password:
                team = {
                    username: {
                        "Password": password,
                        "Total_budget": round(self.total_budget, 1),
                        "Starters_budget": round(self.starters_budget, 1),
                        "Changes_budget": round(self.changes_budget, 1),
                        "Bank_budget": round(self.bank_budget, 1),
                        "Team": self.team,
                        "Team_elements": self.team_elements,
                        "Starters_prices": self.starters_prices,
                        "Changes_prices": self.changes_prices,
                        "Last use": datetime.now().year,
                    }
                }
                saved_teams.update(team)
                with open("saved_teams.json", "w") as data:
                    json.dump(saved_teams, data, indent=4)
                print("\nSave successful.")
            else:
                print("\nThe two passwords don't match. Try again.")

    def save_old_entry(self, new_user: str, saved_teams: dict) -> str:
        """
        Saves on an old entry

        :param new_user: The response of the user on whether he wants to create a new save entry
        :type new_user: str
        :param saved_teams: A dictionary with information on a previously saved team
        :type saved_teams: dict
        :return: The new_user response as a string
        """
        username = ""
        password = ""
        while username not in saved_teams.keys():
            username = input("\nPlease enter your username (or type 'cancel' to go back): ")
            if username in saved_teams.keys():
                while password != saved_teams[username]["Password"]:
                    password = getpass("\nPlease enter your password (or type 'cancel' to go back): ")
                    if password == saved_teams[username]["Password"]:
                        team = {
                            username: {
                                "Password": password,
                                "Total_budget": round(self.total_budget, 1),
                                "Starters_budget": round(self.starters_budget, 1),
                                "Changes_budget": round(self.changes_budget, 1),
                                "Bank_budget": round(self.bank_budget, 1),
                                "Team": self.team,
                                "Team_elements": self.team_elements,
                                "Starters_prices": self.starters_prices,
                                "Changes_prices": self.changes_prices,
                                "Last use": datetime.now().year
                            }
                        }
                        for key in saved_teams.keys():
                            if saved_teams[key]["Last use"] + 1 < datetime.now().year:
                                saved_teams.pop(key, None)
                        saved_teams.update(saved_teams)
                        saved_teams.update(team)
                        with open("saved_teams.json", "w") as data:
                            json.dump(saved_teams, data, indent=4)
                        print("\nSave successful.")
                    elif password.lower() == "cancel":
                        new_user = ""
                        break
                    else:
                        print("\nWrong password.")
            elif username.lower() == "cancel" or password.lower() == "cancel":
                new_user = ""
                break
            else:
                print("\nThis username doesn't exist.")
        return new_user

    def player_checks(self, element: str, player_element: str, used_players_elements: list) -> bool:
        """
        Checks for player parameters in order to update the team or some player list

        :param element: ID of the player in check
        :type element: str
        :param player_element: ID of the player being replaced in the process
        :type player_element: str
        :param used_players_elements: A list of the player elements already used in the loops
        :type used_players_elements: list
        :return: True or False
        """
        if (
            # Check if the player is used (exceeded the team limit while updating)
            element not in used_players_elements
            # Check the excluded players
            and element not in self.unavailable_players_list_elements
            # Check if the player is already in the team
            and element not in self.team_elements
            # Check position
            and self.fpl.player_stat(element, "position") == self.fpl.player_stat(player_element, "position")
        ):
            return True
        else:
            return False

    def manager_pick(self) -> None:
        """
        Updates the lists for picking a potential manager

        :return: None
        """
        self.managers = []
        self.manager_points = []
        self.managers_prices = []
        for manager_element in self.fpl.player_data["id_x"]:
            if (
                self.fpl.player_stat(manager_element, "position") == "MNG"
                and self.fpl.player_stat(manager_element, "cost") <= self.bank_budget
                and self.player_teams.count(self.fpl.player_stat(manager_element, "team")) < 3
            ):
                self.managers.append(self.fpl.player_stat(manager_element, "name"))
                self.manager_points.append(self.fpl.player_stat(manager_element, "manager_points"))
                self.managers_prices.append(self.fpl.player_stat(manager_element, "cost"))
        if len(self.managers) == 0:
            self.managers.append("-")
            self.manager_points.append("-")
            self.managers_prices.append("-")


def update_list(updating_list: list, insert_value: str, remove_value: str) -> None:
    """
    Updates a list's values during player replacement or suggestion processes

    :param updating_list: List to be updated
    :type updating_list: list
    :param insert_value: Value to be inserted in the list
    :type insert_value: str
    :param remove_value: Value to be removed from the list
    :type remove_value: str
    :return: None
    """
    updating_list.insert(0, insert_value)
    updating_list.remove(remove_value)


def enter_budget_choice() -> str:
    """
    Used in the enter_new_team method giving the choice of entering budget information

    :return: A string of 'yes' or 'no'
    """
    budget_choice = ""
    while budget_choice.lower() != "yes" and budget_choice.lower() != "no":
        budget_choice = input("\nDo you want to enter budget information "
                              "along with the team (yes/no/cancel)? ")
        if budget_choice.lower() != "yes" and budget_choice.lower() != "no" and budget_choice.lower() != "cancel":
            print("\nInvalid answer.")
        if budget_choice.lower() == "cancel":
            raise ValueError
    if budget_choice.lower() == "yes" or budget_choice == "no":
        return budget_choice


def enter_player() -> str:
    """
    Requests a player input (used in the enter_new_team method)

    :return: A string of the player name entered
    """
    team_player = input("Add player: ")
    if team_player.lower() == "cancel":
        raise ValueError
    return team_player


def enter_budget(budget_choice: str) -> float:
    """
    Requests selling price in the enter_new_team method if requested by the user

    :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no')
    :type budget_choice: str
    :return: A float of the player's price entered
    """
    player_price = ""
    type_correct = True
    cancel_value = False
    if budget_choice.lower() == "yes":
        while type_correct:
            try:
                player_price_str = input("Add player's selling price: ")
                if player_price_str.lower() == "cancel":
                    cancel_value = True
                    break
                player_price = float(player_price_str)
                if player_price <= 0.0:
                    raise ValueError
                type_correct = False
            except ValueError:
                print("\nInvalid selling price.")
        if cancel_value:
            raise ValueError
        return player_price


def saved_get_username() -> str:
    """
    Gets the username of the user for the open_saved_team method

    :return: A string of the user's username
    """
    username = ""
    with open("saved_teams.json", "r") as data:
        saved_team = json.load(data)
    while username not in saved_team.keys():
        username = input("\nPlease enter your username (or type 'cancel' to go back): ")
        if username.lower() == "cancel":
            raise ValueError
        if username not in saved_team.keys():
            print("\nThis username doesn't exist.")
    return username


def saved_get_password(username: str) -> str:
    """
    Gets the password of the user for the open_saved_team method

    :param username: The user's username
    :type username: str
    :return: A string of the user's password
    """
    password = ""
    with open("saved_teams.json", "r") as data:
        saved_team = json.load(data)
    while password != saved_team[username]["Password"]:
        password = getpass("\nPlease enter your password (or type 'cancel' to go back): ")
        if password.lower() == "cancel":
            raise ValueError
        if password != saved_team[username]["Password"]:
            print("\nWrong password.")
    return password


# if __name__ == "__main__":
#     FPLteam(username, password).compare_players()
