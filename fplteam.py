from fplstats import FPLstats
from itertools import combinations
from unidecode import unidecode
from datetime import datetime
import json
from getpass import getpass


class FPLteam:
    """
    Holds the methods for creating and updating the FPL team.

    Attributes:
        fpl: Calls the FPLstats class for using player stats and calculating points
        team: List of the players of the team
        team_positions: List of the team's players' positions
        player_teams: List of the team's players' Premier League team
        points_sum: Float of the total points calculated for the team based on the program's formula
        player_points: List of the individual players' calculated points
        captain_points: List of the individual player's calculated points for captaincy
        total_budget: Float of the total budget available
        starters_budget: Float of the budget used for the team's starting players
        changes_budget: Float of the budget used for the team's changes
        bank_budget: Float of the budget left in the bank
        starters_prices: List of starting players' prices
        changes_prices: List of changes' price
        unavailable_players_list: List of players excluded from the calculation
        system: List of number of players per position in the team
    """
    def __init__(self):
        self.fpl = FPLstats()

        self.team = []
        self.team_positions = []
        self.player_teams = []
        self.points_sum = 0.0
        self.player_points = []
        self.captain_points = []
        self.total_budget = 100.0
        self.starters_budget = 0.0
        self.changes_budget = 0.0
        self.bank_budget = 0.0
        self.starters_prices = []
        self.changes_prices = []
        self.unavailable_players_list = []
        self.system = [9999, 9999, 9999]

        self.fpl.calculate_points()

    def add_player(self, player: str) -> None:
        """
        Adds a player's statistics to the team lists.

        :param player: Name of the player
        :type player: str
        :return: None
        """
        self.team_positions.append(self.fpl.player_stat(player, "position"))
        self.team.append(player)
        self.points_sum += self.fpl.player_stat(player, "point_calculation")
        self.player_teams.append(self.fpl.player_stat(player, "team"))
        self.starters_budget += round(self.fpl.player_stat(player, "cost"), 1)
        self.bank_budget -= round(self.fpl.player_stat(player, "cost"), 1)
        self.player_points.append(self.fpl.player_stat(player, "point_calculation"))
        self.captain_points.append(self.fpl.player_stat(player, "captain_points"))

    def remove_player(self, player: str) -> None:
        """
        Removes a player's statistics from the lists.

        :param player: Name of the player
        :type player: str
        :return: None
        """
        self.team_positions.pop(self.team.index(player))
        self.points_sum -= self.fpl.player_stat(player, "point_calculation")
        self.player_teams.pop(self.team.index(player))
        self.starters_budget -= round(self.fpl.player_stat(player, "cost"), 1)
        self.bank_budget += round(self.fpl.player_stat(player, "cost"), 1)
        self.player_points.pop(self.team.index(player))
        self.captain_points.pop(self.team.index(player))
        self.team.remove(player)

    def reset_info(self) -> None:
        """
        Resets the starting values of the team class.

        :return: None
        """
        self.team = []
        self.team_positions = []
        self.player_teams = []
        self.points_sum = 0.0
        self.player_points = []
        self.captain_points = []
        self.total_budget = 100.0
        self.starters_budget = 0.0
        self.changes_budget = 0.0
        self.bank_budget = 0.0
        self.starters_prices = []
        self.changes_prices = []
        self.unavailable_players_list = []
        self.system = [9999, 9999, 9999]

    def print_result(self) -> None:
        """
        Prints the results of a calculation in a preferred format.

        :return: None
        """
        print(f"\nIn the bank: {round(self.bank_budget, 1)}")
        print(f"Squad transfer value: {round(self.starters_budget, 1)}")
        print(f"Squad: {self.team}")
        print(f"Potential captains: 1) {self.team[self.captain_points.index(max(self.captain_points))]}"
              f"\t2) {self.team[self.captain_points.index(sorted(self.captain_points)[-2])]}")
        print(f"Total points: {self.points_sum}")
        print(f"Each player's points: {self.player_points}")
        print(f"Captaincy points: {self.captain_points}")

    def create_new_team(self) -> None:
        """
        Calculates a new team without any inputs.

        :return: None
        """
        self.reset_info()
        self.choose_system()
        self.bank_budget = 100.0 - 16.5

        self.create_loop_players()
        self.update_team()

    def enter_new_team(self) -> None:
        """
        Accepts player names and prices in order to create a new team.

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
        Opens a previously saved team.

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

    def open_user_team(self) -> None:
        """
        Opens a new team based on a user's official Fantasy Premier League log-in information.

        :return: None
        """
        self.reset_info()

        status_raise = True
        while status_raise:
            try:
                username = user_get_username()
                password = user_get_password()

                self.user_team_players(username, password)
                self.user_budget_changes(username, password)

                status_raise = False
            except TypeError:
                print("\nInvalid e-mail or password.")

    def compare_players(self) -> None:
        """
        Used for comparing players based on their captaincy points (cost value is not included).

        :return: None
        """
        print("\nThe program will create a list of players that are going to be ranked in the end based on "
              "\ncaptaincy points (meaning that their cost value is not included)."
              "\nPlease type 'stop' when you are done entering player names.\n")
        comparing_players_dict = {}
        add_player = ""
        invalid = False
        while add_player != "stop":
            add_player = input("Give a player's name: ")
            if add_player == "stop":
                break
            for player in self.fpl.player_data["name"]:
                if unidecode(player.lower()) == unidecode(add_player.lower()):
                    comparing_players_dict.update({player: self.fpl.player_stat(player, "captain_points")})
                    invalid = False
                    break
                else:
                    invalid = True
            if invalid:
                print("\nInvalid player name.")
        points_list = list(comparing_players_dict.values())
        points_list.sort(reverse=True)
        sorted_comparing_players_dict = {}
        for number in points_list:
            for name, points in comparing_players_dict.items():
                if number == points:
                    sorted_comparing_players_dict.update({name: points})
        if len(comparing_players_dict) == 0:
            print("")
        else:
            print("\n   Name\t\t\tCaptaincy Points")
            for player in sorted_comparing_players_dict.keys():
                print(f"{points_list.index(sorted_comparing_players_dict[player]) + 1}. {player:21}"
                      f"{round(sorted_comparing_players_dict[player], 2)}")

    def change_players(self) -> None:
        """
        Function for replacing players if excluded.

        :return: None
        """
        # Values that are going to be checked from the team
        changing_players = []
        final_changing_players = []
        temp_teams = [team for team in self.player_teams]
        temp_teams_change = []
        max_budget = []
        used_players = []

        player_budget = self.bank_budget
        for player in self.team:
            if player in self.unavailable_players_list:
                changing_players.append(player)
                final_changing_players.append(player)
                temp_teams_change.append(self.fpl.player_stat(player, "team"))
                player_budget += self.fpl.player_stat(player, "cost")
        max_budget.append(round(player_budget, 1))

        # Main process
        all_teams = self.pl_all_teams()
        for n in range(11):
            # Loop again and retry used players
            self.retry_players(all_teams, used_players)
            for i in range(11):
                # Loop again and retry all players
                # (basically try the players that might have been suitable before the change by looping again)
                for team_player in changing_players:
                    if team_player in self.team or team_player in used_players:
                        # First check replacing players without checking points just to remove them
                        self.change_players_first_loop(
                            used_players, changing_players, team_player, max_budget, temp_teams, temp_teams_change
                        )
                    else:
                        self.change_players_more_loops(
                            used_players, changing_players, team_player, max_budget, temp_teams, temp_teams_change
                        )
        for team_player in changing_players:
            self.add_player(team_player)
        for player in final_changing_players:
            self.remove_player(player)
        self.print_result()

    def update_team(self) -> None:
        """
        Updates the entire FPL team.

        :return: None
        """
        all_teams = self.pl_all_teams()

        used_players = []
        max_budget = round(self.total_budget - 16.5, 1)

        for n in range(11):
            # Loop again and retry used players
            self.retry_players(all_teams, used_players)
            for i in range(11):
                # Loop again and retry all players
                # (basically try the players that might have been suitable before the change by looping again)
                for team_player in self.team:
                    if team_player in self.unavailable_players_list or team_player in used_players:
                        # First check replacing players without checking points just to remove them
                        self.update_team_first_loop(used_players, team_player, max_budget)
                    else:
                        self.update_team_more_loops(used_players, team_player, max_budget)
        self.print_result()

    def transfer_players(self) -> None:
        """
        Used for transferring players and hold information on player availability.

        :return: None
        """
        continue_updating = ""
        while continue_updating.lower() != "skip":
            continue_updating = input("\nDo you want to exclude any players or get suggestion "
                                      "(exclude/suggestion/skip)? ")
            if continue_updating.lower() == "exclude":
                break
            elif continue_updating.lower() == "skip":
                return None
            elif continue_updating.lower() == "suggestion":
                self.transfer_calculation()
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
        ):
            invalid_check.clear()
            unavailable_player = input("\nAdd players to the exclusion list "
                                       "(player/suggestion/all/update/none/stop): ")
            if unavailable_player.lower() == "stop":
                break
            if unavailable_player.lower() == "none":
                self.unavailable_players_list = []
                break
            for player in self.team:
                if unavailable_player.lower() == "all" and player not in self.unavailable_players_list:
                    self.unavailable_players_list.append(player)
            if unavailable_player.lower() == "update":
                self.update_team()
                self.transfer_players()
                return None
            if unavailable_player.lower() == "suggestion":
                self.transfer_calculation()
                self.transfer_players()
                return None
            for name in self.fpl.player_data["name"]:
                if unidecode(unavailable_player.lower()) == unidecode(self.fpl.player_stat(name, "name").lower()):
                    if name not in self.unavailable_players_list:
                        self.unavailable_players_list.append(name)
                        break
                    else:
                        print("\nThe player is already excluded.")
            for name in self.fpl.player_data["name"]:
                if (
                    unidecode(unavailable_player.lower()) != unidecode(self.fpl.player_stat(name, "name").lower())
                    and unavailable_player.lower() != "all"
                    and unavailable_player.lower() != "update"
                    and unavailable_player.lower() != "suggestion"
                ):
                    invalid_check.append(1)
                else:
                    invalid_check.append(0)
            if 0 not in invalid_check:
                print("\nInvalid answer.")
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
                    self.update_team()
                    self.transfer_players()
                    return None
                elif unavailable_player.lower() == "stop":
                    changes_choice = ""
                    while changes_choice.lower() != "replace" and changes_choice.lower() != "update":
                        changes_choice = input("\nDo you want to find replacements "
                                               "or update the entire team (replace/update)? ")
                        if changes_choice.lower() == "replace":
                            self.change_players()
                            self.transfer_players()
                            return None
                        elif changes_choice.lower() == "update":
                            self.update_team()
                            self.transfer_players()
                            return None
                        else:
                            print("\nInvalid answer.")
            elif 1 in player_not_in_team:
                self.transfer_players()
                return None

    def transfer_calculation(self) -> None:
        """
        Calculates whether an extra player transfer is worth the -4 points and gives a list of suggestions.

        :return: None
        """
        # Calculation for single transfer
        self.transfer_single_loop()

        extended_suggestion = ""
        while extended_suggestion.lower() != "yes" and extended_suggestion.lower() != "no":
            extended_suggestion = input("\nWould you like to run the extended suggestion "
                                        "for double player changes (yes/no)? ")
            if extended_suggestion.lower() != "yes" and extended_suggestion.lower() != "no":
                print("\nInvalid answer.")
            if extended_suggestion.lower() == "yes":
                # Calculation for double transfer
                self.transfer_double_loop()

    def choose_system(self) -> None:
        """
        Holds information on the team's system.

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
        Saves the team for future use.

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

    def create_loop_players(self) -> None:
        """
        Loops through the player database to create a team in the create_new_team method.

        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                # Check team limit
                self.player_teams.count(self.fpl.player_stat(name, "team")) > 2
                # Check position limit
                or self.fpl.player_stat(name, "position") == "GKP"
                and self.team_positions.count("GKP") == 1
                or self.fpl.player_stat(name, "position") == "DEF"
                and self.team_positions.count("DEF") == self.system[0]
                or self.fpl.player_stat(name, "position") == "MID"
                and self.team_positions.count("MID") == self.system[1]
                or self.fpl.player_stat(name, "position") == "FWD"
                and self.team_positions.count("FWD") == self.system[2]
            ):
                continue
            else:
                self.add_player(name)

    def enter_loop_players(self, team_player: str, budget_choice: str, player_price: float) -> None:
        """
        Loops through the player database in search of the player name given and add him to the team
        (used in the enter_new_team method).

        :param team_player: Name of the player the method searches for.
        :type team_player: str
        :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no').
        :type budget_choice: str
        :param player_price: Price of the player the method searches for.
        :type player_price: float
        :return: None
        """
        invalid = False
        for player in self.fpl.player_data["name"]:
            if (
                # Check if the player exists
                unidecode(player.lower()) == unidecode(team_player.lower())
                # Check if the player is already in the team
                and player not in self.team
                # Check team limit
                and self.player_teams.count(self.fpl.player_stat(player, "team")) < 3
                # Check position limit
                and (
                     self.fpl.player_stat(player, "position") == "GKP"
                     and self.team_positions.count("GKP") < 1
                     or self.fpl.player_stat(player, "position") == "DEF"
                     and self.team_positions.count("DEF") < self.system[0]
                     or self.fpl.player_stat(player, "position") == "MID"
                     and self.team_positions.count("MID") < self.system[1]
                     or self.fpl.player_stat(player, "position") == "FWD"
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
                        self.fpl.fplapi.main_df["name"] == player], ["cost"]
                    ] = player_price
                    self.starters_prices.append(player_price)
                self.add_player(player)
                invalid = False
                break
            else:
                invalid = True
        if invalid:
            print("\nInvalid player name.")

    def enter_budget_changes(self, budget_choice: str) -> None:
        """
        Changes the budget values if used (in the enter_new_team method).

        :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no').
        :type budget_choice: str
        :return: None
        """
        if budget_choice.lower() == "no":
            self.bank_budget += 100.0 - 16.5

        if budget_choice.lower() == "yes":
            self.starters_budget = round(sum(self.starters_prices), 1)

        changes_budget = ""
        type_error = True
        if budget_choice.lower() == "yes":
            while type_error:
                try:
                    changes_budget = float(input("Enter your changes' budget: "))
                    type_error = False
                except ValueError:
                    print("\nInvalid budget.")
            self.changes_budget = changes_budget

        bank_budget = ""
        type_error = True
        if budget_choice.lower() == "yes":
            while type_error:
                try:
                    bank_budget = float(input("Enter your budget in the bank: "))
                    type_error = False
                except ValueError:
                    print("\nInvalid budget.")
            self.bank_budget = bank_budget

        if budget_choice.lower() == "yes":
            self.total_budget = round(self.starters_budget + self.changes_budget + self.bank_budget, 1)

    def saved_loop_players(self, saved_team: dict, username: str) -> None:
        """
        Loops through the player database in search of the players in the saved team file and updates the team
        (used in the open_saved_team method).

        :param saved_team: Dictionary of the saved team taken from the .json file.
        :type saved_team: dict
        :param username: The user's username.
        :type username: str
        :return:
        """
        # Changing the player cost in the main_df based on the selling price we get
        # from the saved_team
        # The functionality of changing the main_df here is based on the fact that the
        # info of the main_df is stored in the cache and the fpl_player_stats function
        # just calls the result from there without running again
        # (a bit of cheating someone might say... *sips tea sardonically*)
        for player in saved_team[username]["Team"]:
            self.fpl.fplapi.main_df.loc[self.fpl.fplapi.main_df.index[
                self.fpl.fplapi.main_df["name"] == player], ["cost"]] = saved_team[username]["Starters_prices"][
                saved_team[username]["Team"].index(player)]
        for player in saved_team[username]["Team"]:
            self.add_player(player)

    def saved_budget_changes(self, saved_team: dict, username: str) -> None:
        """
        Changes the budget values in the open_saved_team method.

        :param saved_team: Dictionary of the saved team taken from the .json file.
        :type saved_team: dict
        :param username: The user's username.
        :type username: str
        :return: None
        """
        self.total_budget = round(saved_team[username]["Total_budget"], 1)
        self.starters_budget = round(saved_team[username]["Starters_budget"], 1)
        self.changes_budget = round(saved_team[username]["Changes_budget"], 1)
        self.bank_budget = round(saved_team[username]["Bank_budget"], 1)
        self.starters_prices = saved_team[username]["Starters_prices"]
        self.changes_prices = saved_team[username]["Changes_prices"]

    def user_team_players(self, username: str, password: str) -> None:
        """
        Gets the user's team from the official FPL API using his log-in information
        (used in the open_user_team method).

        :param username: The user's username.
        :type username: str
        :param password: The user's password.
        :type password: str
        :return: None
        """
        team_list_elements = self.fpl.fplapi.get_team(username, password)["team_elements"]
        team_list = (
            [self.fpl.player_data["name"][element == self.fpl.player_data["id_x"]]
             [self.fpl.player_data.index[element == self.fpl.player_data["id_x"]].tolist()[0]]
             for element in team_list_elements]
        )
        team_starters = []
        for number in range(11):
            team_starters.append(team_list[number])
        for player in team_starters:
            self.add_player(player)

    def user_budget_changes(self, username: str, password: str) -> None:
        """
        Changes the budget values in the open_user_team method.

        :param username: The user's username from his official FPL account.
        :type username: str
        :param password: The user's password from his official FPL account.
        :type password: str
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
        Creates a list of all the premier league teams.

        :return: A list of all the premier league teams.
        """
        all_teams = []
        for team in self.fpl.player_data["team"]:
            if team not in all_teams:
                all_teams.append(team)
        return all_teams

    def retry_players(self, all_teams: list, used_players: list) -> None:
        """
        Makes the player available for the team again if his premier league team doesn't appear more than 2 times in
        the players' teams count according to the FPL rules.

        :param all_teams: A list of all the premier league teams.
        :type all_teams: list
        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :return: None
        """
        for team in all_teams:
            if self.player_teams.count(team) < 3:
                for player in used_players:
                    if self.fpl.player_stat(player, "team") == team:
                        used_players.remove(player)

    def change_players_first_loop(
            self, used_players: list, changing_players: list, team_player: str, max_budget: list,
            temp_teams: list, temp_teams_change: list
    ) -> None:
        """
        First loop through players in the change_players method. Just replacing the original changing players.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param changing_players: A list of the players in the process of changing.
        :type changing_players: list
        :param team_player: A player from the changing_players list.
        :type team_player: str
        :param max_budget: A list containing the maximum budget for the player change.
        :type max_budget: list
        :param temp_teams: A list of the team's players' premier league teams.
        :type temp_teams: list
        :param temp_teams_change: A list of the changing players' premier league teams.
        :type temp_teams_change: list
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                self.player_checks(name, team_player, used_players)
                # Check if the player is already in the players that are about to change
                and name not in changing_players
                # Check for valid points
                and self.fpl.player_stat(name, "point_calculation") > 0
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(name, "cost")
                     + sum([self.fpl.player_stat(player, "cost") for player in changing_players
                            if player != team_player])
                    ), 1
                )
                if temporary_budget <= max_budget[0]:
                    # Checking the budget limit
                    player_team_number = (temp_teams.count(self.fpl.player_stat(name, "team")))
                    if self.fpl.player_stat(name, "team") == temp_teams_change[changing_players.index(team_player)]:
                        # Check team limit
                        if player_team_number < 4:
                            update_list(changing_players, name, team_player)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )
                            break
                    else:
                        if player_team_number < 3:
                            update_list(changing_players, name, team_player)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )
                            break

    def change_players_more_loops(
            self, used_players: list, changing_players: list, team_player: str, max_budget: list,
            temp_teams: list, temp_teams_change: list
    ) -> None:
        """
        Loops after the first loop through players in the change_players method.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param changing_players: A list of the players in the process of changing.
        :type changing_players: list
        :param team_player: A player from the changing_players list.
        :type team_player: str
        :param max_budget: A list containing the maximum budget for the player change.
        :type max_budget: list
        :param temp_teams: A list of the team's players' premier league teams.
        :type temp_teams: list
        :param temp_teams_change: A list of the changing players' premier league teams.
        :type temp_teams_change: list
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                self.player_checks(name, team_player, used_players)
                # Check if the player is already in the players that are about to change
                and name not in changing_players
                # Check for valid points
                and self.fpl.player_stat(name, "point_calculation") > 0
                # Check for better points
                and sum([self.fpl.player_stat(player, "point_calculation")
                         for player in changing_players])
                < self.fpl.player_stat(name, "point_calculation")
                + sum([self.fpl.player_stat(player, "point_calculation")
                       for player in changing_players if player != team_player])
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(name, "cost")
                     + sum([self.fpl.player_stat(player, "cost") for player in changing_players
                            if player != team_player])
                    ), 1
                )
                if temporary_budget <= max_budget[0]:
                    # Checking the budget limit
                    player_team_number = (temp_teams.count(self.fpl.player_stat(name, "team")))
                    if self.fpl.player_stat(name, "team") == (temp_teams_change[changing_players.index(team_player)]):
                        # Check team limit
                        if player_team_number < 4:
                            update_list(changing_players, name, team_player)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )
                            break
                    else:
                        if self.fpl.player_stat(name, "team") in temp_teams_change:
                            # Check for players on the team limit in order to pick the best ones in the
                            # next loop
                            for player in changing_players:
                                if (
                                    # Checking for players other than the player that's currently
                                    # updating
                                    player != team_player
                                    # Check for better points
                                    and self.fpl.player_stat(player, "point_calculation")
                                    > self.fpl.player_stat(name, "point_calculation") > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Check team
                                    and self.fpl.player_stat(player, "team") == self.fpl.player_stat(name, "team")
                                    # Don't enter the name twice in the list
                                    and name not in used_players
                                ):
                                    used_players.append(name)
                                elif (
                                      # Checking for players other than the player that's currently
                                      # updating
                                      player != team_player
                                      # Check for better points
                                      and 0 < self.fpl.player_stat(player, "point_calculation")
                                      < self.fpl.player_stat(name, "point_calculation")
                                      # Check team limit
                                      and player_team_number > 2
                                      # Check team
                                      and self.fpl.player_stat(player, "team") == self.fpl.player_stat(name, "team")
                                      # Don't enter the name twice in the list
                                      and player not in used_players
                                ):
                                    used_players.append(player)
                        if player_team_number < 3:
                            update_list(changing_players, name, team_player)

                            update_list(
                                temp_teams_change, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )

                            update_list(
                                temp_teams, self.fpl.player_stat(name, "team"),
                                self.fpl.player_stat(team_player, "team")
                            )
                            break

    def update_team_first_loop(self, used_players: list, team_player: str, max_budget: float) -> None:
        """
        First loop through players in the update_team method. Just replacing the original players.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param team_player: A player from the team list.
        :type team_player: str
        :param max_budget: A float of the maximum budget for the team.
        :type max_budget: float
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if self.player_checks(name, team_player, used_players):
                temporary_budget = round(
                    (
                     self.starters_budget
                     + self.fpl.player_stat(name, "cost")
                     - self.fpl.player_stat(team_player, "cost")
                    ), 1
                )
                if temporary_budget <= max_budget:
                    # Checking the budget limit
                    player_team_number = (self.player_teams.count(self.fpl.player_stat(name, "team")))
                    if self.fpl.player_stat(name, "team") == self.player_teams[self.team.index(team_player)]:
                        # Check team limit
                        if player_team_number < 4:
                            self.add_player(name)
                            self.remove_player(team_player)
                            break
                    else:
                        if player_team_number < 3:
                            self.add_player(name)
                            self.remove_player(team_player)
                            break

    def update_team_more_loops(self, used_players: list, team_player: str, max_budget: float) -> None:
        """
        Loops after the first loop through players in the update_team method.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param team_player: A player from the team list.
        :type team_player: str
        :param max_budget: A float of the maximum budget for the team.
        :type max_budget: float
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                self.player_checks(name, team_player, used_players)
                # Check for better points
                and self.fpl.player_stat(name, "point_calculation")
                > self.player_points[self.team.index(team_player)]
            ):
                temporary_budget = round(
                    (
                     self.starters_budget
                     + self.fpl.player_stat(name, "cost")
                     - self.fpl.player_stat(team_player, "cost")
                    ), 1
                )
                if temporary_budget <= max_budget:
                    # Checking the budget limit
                    player_team_number = (self.player_teams.count(self.fpl.player_stat(name, "team")))
                    if (
                        self.fpl.player_stat(name, "team")
                        == self.player_teams[self.team.index(team_player)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            self.add_player(name)
                            self.remove_player(team_player)
                            break
                    else:
                        if self.fpl.player_stat(name, "team") in self.player_teams:
                            # Check for players on the team limit in order to pick the best ones in the
                            # next loop
                            for player in self.team:
                                if (
                                    # Checking for players other than the player that's currently
                                    # updating
                                    player != team_player
                                    # Check for better points
                                    and self.fpl.player_stat(player, "point_calculation")
                                    > self.fpl.player_stat(name, "point_calculation") > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Check team
                                    and self.fpl.player_stat(player, "team")
                                    == self.fpl.player_stat(name, "team")
                                    # Don't enter the name twice in the list
                                    and name not in used_players
                                ):
                                    used_players.append(name)
                                elif (
                                      # Checking for players other than the player that's currently
                                      # updating
                                      player != team_player
                                      # Check for better points
                                      and 0 < self.fpl.player_stat(player, "point_calculation")
                                      < self.fpl.player_stat(name, "point_calculation")
                                      # Check team limit
                                      and player_team_number > 2
                                      # Check team
                                      and self.fpl.player_stat(player, "team") == self.fpl.player_stat(name, "team")
                                      # Don't enter the name twice in the list
                                      and player not in used_players
                                ):
                                    used_players.append(player)
                        if player_team_number < 3:
                            self.add_player(name)
                            self.remove_player(team_player)
                            break

    def transfer_single_loop(self) -> None:
        """
        Single transfer suggestion loop.

        :return: None
        """
        max_budget_single_transfer = round(self.total_budget - 16.5, 1)
        used_players = []
        for player in self.team:
            possible_transfers = {}
            for name in self.fpl.player_data["name"]:
                if (
                    self.player_checks(name, player, used_players)
                    # Check for better transfer points
                    and self.fpl.player_stat(name, "transfer_points") >= self.player_points[self.team.index(player)]
                ):
                    temporary_budget = round(
                        (
                         self.starters_budget
                         + self.fpl.player_stat(name, "cost")
                         - self.fpl.player_stat(player, "cost")
                        ), 1
                    )
                    if temporary_budget <= max_budget_single_transfer:
                        # Checking the budget limit
                        player_team_number = (
                            self.player_teams.count(self.fpl.player_stat(name, "team"))
                        )
                        if (
                            self.fpl.player_stat(name, "team")
                            == self.player_teams[self.team.index(player)]
                        ):
                            # Check team limit
                            if player_team_number < 4:
                                transfer_per_dif = round(
                                    (self.fpl.player_stat(name, "transfer_points")
                                     / (self.fpl.player_stat(name, "transfer_points")
                                        + self.fpl.player_stat(player, "point_calculation"))) * 100, 2
                                )
                                possible_transfers.update({name: transfer_per_dif})
                        else:
                            if player_team_number < 3:
                                transfer_per_dif = round(
                                    (self.fpl.player_stat(name, "transfer_points")
                                     / (self.fpl.player_stat(name, "transfer_points")
                                        + self.fpl.player_stat(player, "point_calculation"))) * 100, 2
                                )
                                possible_transfers.update({name: transfer_per_dif})
            percentage_list = list(possible_transfers.values())
            percentage_list.sort(reverse=True)
            sorted_possible_transfers = {}
            for number in percentage_list:
                for name, percentage in possible_transfers.items():
                    if number == percentage:
                        sorted_possible_transfers.update({name: percentage})
            print(f"\nPossible transfers for {player}: ")
            if len(possible_transfers) == 0:
                print("-")
            else:
                print("Name\t\t\tBetter Value Possibility")
                for name in sorted_possible_transfers:
                    print(f"{name:<24}{sorted_possible_transfers[name]} %")

    def transfer_double_first_loop(self, used_players: list, possible_transfers: dict, key: int, team_player: str,
                                   max_budget: list, teams: list, teams_transfer: list) -> None:
        """
        Double transfer suggestion first loop through players.
        Just replacing the original players of the possible transfer.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param possible_transfers: A dictionary of the possible double transfer combinations.
        :type possible_transfers: dict
        :param key: The key of the possible_transfers dictionary.
        :type key: int
        :param team_player: A player from the team list.
        :type team_player: str
        :param max_budget: A list of the possible max budgets.
        :type max_budget: list
        :param teams: A list of the premier league teams of the players in the team, which updates while transfer
        calculations are taking place.
        :type teams: list
        :param teams_transfer: A list of the premier league teams of the players in the possible_transfers dictionary.
        :type teams_transfer: list
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                self.player_checks(name, team_player, used_players)
                # Check if the name is already in the changing duo
                and name not in possible_transfers[key]
                # Check for valid transfer points
                and self.fpl.player_stat(name, "transfer_points") > 0
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(name, "cost")
                     + sum([self.fpl.player_stat(player, "cost")
                            for player in possible_transfers[key]
                            if player != team_player])
                    ), 1
                )
                if temporary_budget <= max_budget[key]:
                    # Checking the budget limit
                    player_team_number = (teams.count(self.fpl.player_stat(name, "team")))
                    if (
                        self.fpl.player_stat(name, "team")
                        == teams_transfer[0][possible_transfers[key].index(team_player)]
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            possible_transfers[key] = list(map(lambda x: x.replace(team_player, name),
                                                               possible_transfers[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(name, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                team_player, "team"))

                            teams.append(self.fpl.player_stat(name, "team"))
                            teams.remove(self.fpl.player_stat(team_player, "team"))
                            break
                    else:
                        if player_team_number < 3:
                            possible_transfers[key] = list(map(lambda x: x.replace(team_player, name),
                                                               possible_transfers[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(name, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                team_player, "team"))

                            teams.append(self.fpl.player_stat(name, "team"))
                            teams.remove(self.fpl.player_stat(team_player, "team"))
                            break

    def transfer_double_more_loops(self, used_players: list, possible_transfers: dict, key: int, team_player: str,
                                   max_budget: list, teams: list, teams_transfer: list) -> None:
        """
        Double transfer suggestion loops after the first loop through players.

        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :param possible_transfers: A dictionary of the possible double transfer combinations.
        :type possible_transfers: dict
        :param key: The key of the possible_transfers dictionary.
        :type key: int
        :param team_player: A player from the team list.
        :type team_player: str
        :param max_budget: A list of the possible max budgets.
        :type max_budget: list
        :param teams: A list of the premier league teams of the players in the team, which updates while transfer
        calculations are taking place.
        :type teams: list
        :param teams_transfer: A list of the premier league teams of the players in the possible_transfers dictionary.
        :type teams_transfer: list
        :return: None
        """
        for name in self.fpl.player_data["name"]:
            if (
                self.player_checks(name, team_player, used_players)
                # Check if the name is already in the changing duo
                and name not in possible_transfers[key]
                # Check for valid transfer points
                and self.fpl.player_stat(name, "transfer_points") > 0
                # Check for better transfer points
                and sum([self.fpl.player_stat(player, "transfer_points")
                         for player in possible_transfers[key]])
                < self.fpl.player_stat(name, "transfer_points")
                + [self.fpl.player_stat(player, "transfer_points")
                   for player in possible_transfers[key] if player != team_player]
            ):
                temporary_budget = round(
                    (
                     self.fpl.player_stat(name, "cost")
                     + sum([self.fpl.player_stat(player, "cost")
                            for player in possible_transfers[key]
                            if player != team_player])
                    ), 1
                )
                if temporary_budget <= max_budget[key]:
                    # Checking the budget limit
                    player_team_number = (teams.count(self.fpl.player_stat(name, "team")))
                    if (
                        self.fpl.player_stat(name, "team")
                        == (teams_transfer[0][possible_transfers[key].index(team_player)])
                    ):
                        # Check team limit
                        if player_team_number < 4:
                            possible_transfers[key] = list(map(lambda x: x.replace(team_player, name),
                                                               possible_transfers[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(name, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                team_player, "team"))

                            teams.append(self.fpl.player_stat(name, "team"))
                            teams.remove(self.fpl.player_stat(
                                team_player, "team"))
                            break
                    else:
                        if self.fpl.player_stat(name, "team") in teams_transfer[0]:
                            # Check for players on the team limit in order to pick the
                            # best ones in the next loop
                            for player in possible_transfers[key]:
                                if (
                                    # Checking for players other than the player
                                    # that's currently updating
                                    player != team_player
                                    # Check for better transfer points
                                    and self.fpl.player_stat(player, "transfer_points")
                                    > self.fpl.player_stat(name, "transfer_points") > 0
                                    # Check team limit
                                    and player_team_number > 2
                                    # Don't enter the name twice in the list
                                    and name not in used_players
                                ):
                                    used_players.append(name)
                                elif (
                                      # Checking for players other than the player
                                      # that's currently updating
                                      player != team_player
                                      # Check for better transfer points
                                      and 0 < self.fpl.player_stat(player, "transfer_points")
                                      < self.fpl.player_stat(name, "transfer_points")
                                      # Check team limit
                                      and player_team_number > 2
                                      # Don't enter the name twice in the list
                                      and player not in used_players
                                ):
                                    used_players.append(player)
                        if player_team_number < 3:
                            possible_transfers[key] = list(map(lambda x: x.replace(team_player, name),
                                                               possible_transfers[key]))

                            teams_transfer[0].insert(0, self.fpl.player_stat(name, "team"))
                            teams_transfer[0].remove(self.fpl.player_stat(
                                team_player, "team"))

                            teams.append(self.fpl.player_stat(name, "team"))
                            teams.remove(self.fpl.player_stat(
                                team_player, "team"))
                            break

    def transfer_double_loop(self) -> None:
        """
        Double transfer suggestion loop.

        :return: None
        """
        # Combinations of 2 from the team
        possible_transfers = self.transfer_combinations()

        # Values that are going to be checked from the team
        max_budget = []
        starting_transfer_points_list = []
        for key in possible_transfers.keys():
            player_budget = self.bank_budget
            for player in possible_transfers[key]:
                player_budget += self.fpl.player_stat(player, "cost")
            max_budget.append(round(player_budget, 1))
            changing_player_points = [self.fpl.player_stat(player, "point_calculation")
                                      for player in possible_transfers[key]]
            starting_transfer_points_list.append(changing_player_points)
        all_teams = self.pl_all_teams()

        for key in possible_transfers.keys():
            # Loop on all duo combinations
            used_players = []
            teams_transfer = []
            teams = [x for x in self.player_teams]
            teams_transfer.append([self.fpl.player_stat(possible_transfers[key][0], "team"),
                                   self.fpl.player_stat(possible_transfers[key][1], "team")])
            print(f"\nPossible transfers for {possible_transfers[key]}:")
            for n in range(11):
                # Loop again and retry used players
                self.retry_players(all_teams, used_players)
                for i in range(11):
                    # Loop again and retry all players
                    # (basically try the players that might have been suitable before the change
                    # by looping again)
                    for team_player in possible_transfers[key]:
                        if team_player in self.team or team_player in used_players:
                            # First check replacing players without checking points just to remove them
                            self.transfer_double_first_loop(used_players, possible_transfers, key, team_player,
                                                            max_budget, teams, teams_transfer)
                        else:
                            self.transfer_double_more_loops(used_players, possible_transfers, key, team_player,
                                                            max_budget, teams, teams_transfer)

            final_transfer_points = [self.fpl.player_stat(player, "transfer_points")
                                     for player in possible_transfers[key]]
            value_possibility = round(((final_transfer_points[0] / (final_transfer_points[0]
                                                                    + starting_transfer_points_list[key][0]))
                                       + (final_transfer_points[1] / (final_transfer_points[1]
                                                                      + starting_transfer_points_list[key][1])))
                                      / 2 * 100, 2)
            if value_possibility < 50:
                print("-")
            else:
                player_string = "["
                for player in possible_transfers[key]:
                    player_string += f"'{player}', "
                player_string = player_string[:-2] + "]"
                print("Players\t\t\t\t\tBetter Value Possibility")
                print(f"{player_string:<40}{value_possibility} %")

    def transfer_combinations(self) -> dict:
        """
        Calculates all the possible duos from the team.

        :return: A dictionary of possible double transfers from the team.
        """
        possible_transfers = {}
        i = 0
        for players in combinations(self.team, 2):
            players = list(players)
            possible_transfers.update({i: players})
            i += 1
        return possible_transfers

    def save_new_entry(self) -> None:
        """
        Creates a new save entry.

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
                        "Starters_prices": self.starters_prices,
                        "Changes_prices": self.changes_prices,
                        "Last use": datetime.now().year
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
        Saves on an old entry.

        :param new_user: The response of the user on whether he wants to create a new save entry.
        :type new_user: str
        :param saved_teams: A dictionary with information on a previously saved team.
        :type saved_teams: dict
        :return: The new_user response as a string.
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

    def player_checks(self, name: str, team_player: str, used_players: list) -> bool:
        """
        Checks for player parameters in order to update the team or some player list.

        :param name: Name of the player in check.
        :type name: str
        :param team_player: Name of the player being replaced in the process.
        :type team_player: str
        :param used_players: A list of the players already used in the loops.
        :type used_players: list
        :return: True or False
        """
        if (
            # Check if the player is used (exceeded the team limit while updating)
            name not in used_players
            # Check the excluded players
            and name not in self.unavailable_players_list
            # Check if the player is already in the team
            and name not in self.team
            # Check position
            and self.fpl.player_stat(name, "position") == self.fpl.player_stat(team_player, "position")
        ):
            return True
        else:
            return False


def update_list(updating_list: list, insert_value: str, remove_value: str) -> None:
    """
    Updates a list's values during player replacement or suggestion processes.

    :param updating_list: List to be updated.
    :type updating_list: list
    :param insert_value: Value to be inserted in the list.
    :type insert_value: str
    :param remove_value: Value to be removed from the list.
    :type remove_value: str
    :return: None
    """
    updating_list.insert(0, insert_value)
    updating_list.remove(remove_value)


def enter_budget_choice() -> str:
    """
    Used in the enter_new_team method giving the choice of entering budget information.

    :return: A string of 'yes' or 'no'.
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
    Requests a player input (used in the enter_new_team method).

    :return: A string of the player name entered.
    """
    team_player = input("Add player: ")
    if team_player.lower() == "cancel":
        raise ValueError
    return team_player


def enter_budget(budget_choice: str) -> float:
    """
    Requests selling price in the enter_new_team method if requested by the user.

    :param budget_choice: Choice of whether to enter budget information or not ('yes' or 'no').
    :type budget_choice: str
    :return: A float of the player's price entered.
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
    Gets the username of the user for the open_saved_team method.

    :return: A string of the user's username.
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
    Gets the password of the user for the open_saved_team method.

    :param username: The user's username.
    :type username: str
    :return: A string of the user's password.
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


def user_get_username() -> str:
    """
    Gets the username of the user's official FPL account for the open_user_team method.

    :return: A string of the user's username.
    """
    username = input("\nPlease enter your e-mail (or type 'cancel' to go back): ")
    if username.lower() == "cancel":
        raise ValueError
    return username


def user_get_password() -> str:
    """
    Gets the password of the user's official FPL account for the open_user_team method.

    :return: A string of the user's password.
    """
    password = getpass("\nPlease enter your password (or type 'cancel' to go back): ")
    if password.lower() == "cancel":
        raise ValueError
    return password


if __name__ == "__main__":
    test_name = saved_get_username()
    print(saved_get_password(test_name))
