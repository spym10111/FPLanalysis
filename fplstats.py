import numpy as np
import fplapi
from fplapi import FPLapi
import json
from datetime import datetime
from functools import cache

MIN_GW_NUMBER = 1
MAX_GW_NUMBER = 38


class FPLstats:
    """
    Holds the methods for calculating the FPL statistics

    Attributes:
        fplapi: Calls the FPLapi class for getting information from the official source of the Fantasy Premier League
        player_data: Calls the method for the official Fantasy Premier League stats
        fdr_data: Calls the method for the official Fantasy Premier League FDR
    """
    def __init__(self, username, password):
        # Getting the Dataframes
        self.fplapi = FPLapi(username, password)
        self.player_data = self.fplapi.fpl_player_stats()
        self.fdr_data = self.fplapi.fpl_fdr()
        self.last_gw_number = 0
        np.set_printoptions(legacy="1.25")

    def calculate_points(self) -> None:
        """
        Calculates the stats that are taken into account when creating the team or searching for players. The results
        are stored in the players Dataframe created in the fplapi.py

        :return: None
        """
        # Number of GWs to calculate
        fdr_range = fdr_input()
        fdr_gw = calculate_fdr(fdr_range[0], fdr_range[1])
        # Number of GWs the statistics correspond to
        self.last_gw_number = fplapi.gw_played()
        # Calculating the FDR part of the function
        self.fdr_product(fdr_gw)

        # The functions used for team selection
        self.player_data["bonus_new"] = self.player_data["bonus"] + 1
        self.player_data["form_new"] = self.player_data["form"].astype(float) + (1/1000)
        # Calculating points for player comparison
        self.point_calculation(fdr_range[0], fdr_range[1])
        # Calculating points for captaincy comparison
        self.captain_points(fdr_range[0], fdr_range[1])
        # Calculating points for transfer comparison
        self.transfer_points(self.last_gw_number, fdr_range[0], fdr_range[1])
        # Calculating points for manager comparison
        self.manager_points(fdr_range[0], fdr_range[1])

        self.player_data.sort_values(by=["point_calculation", "points_per_game"], ascending=False)

    @cache
    def player_stat(self, player_element: str, statistic_value: str):
        """
        Returns a specific player's stat

        :param player_element: Player ID
        :type player_element: str
        :param statistic_value: Type of stat returned
        :type statistic_value: str
        :return: A specific stat for a specific player
        """
        return (
            self.player_data[statistic_value]
            [self.player_data.index[self.player_data["id_x"] == player_element].tolist()[0]]
        )

    def fdr_product(self, fdr_gw: list) -> None:
        """
        Calculates the FDR part of the function

        :param fdr_gw: A list of the first and last GWs included in the calculations
        :type fdr_gw: list
        :return: None
        """
        fdr_index = []
        for player_team in self.player_data["team"]:
            fdr_index.append(self.fdr_data.index[self.fdr_data["team"] == player_team].tolist()[0])

        # Calculating FDR for multiple GWs
        fdr_rows = []
        fdr_final = 0
        fdr_final_list = []
        fdr_final_list_calc = []
        for gw in fdr_gw:
            fdr_rows.append(self.fdr_data[gw].tolist())
        if len(fdr_rows) == 1:
            fdr_final_list_calc = fdr_rows[0]
            for fdr_value in fdr_final_list_calc:
                if np.isnan(fdr_value):
                    fdr_final_list_calc[fdr_final_list_calc.index(fdr_value)] = 9999
        else:
            for i in range(20):
                fdr_final_sublist = []
                for row in fdr_rows:
                    fdr_final_sublist.append(row[0])
                    row.pop(0)
                fdr_final_list.append(fdr_final_sublist)
            for team_fdr in fdr_final_list:
                i = 0
                for fdr_value in team_fdr:
                    if np.isnan(fdr_value):
                        continue
                    if i == 0 and not np.isnan(fdr_value):
                        fdr_final = fdr_value
                    else:
                        fdr_final = fdr_final * fdr_value / (fdr_final + fdr_value)
                    i += 1
                fdr_final_list_calc.append(fdr_final)
                fdr_final = 0
        self.fdr_data["final"] = fdr_final_list_calc
        self.player_data["fdr_final"] = ""
        new_fdr_final_list = self.player_data["fdr_final"].to_list()
        for i in range(len(new_fdr_final_list)):
            new_fdr_final_list[i] = self.fdr_data["final"].to_list()[fdr_index[i]]
        self.player_data["fdr_final"] = new_fdr_final_list

    def calculation_factors(self) -> None:
        """
        Used to calculate the point formula factors for every value. Creates a .json file with the values

        :return: None
        """
        try:
            with open("factors.json", "r") as data:
                factors = json.load(data)
        except FileNotFoundError:
            factors_dict_start = {}
            for gw_start in range(1, 39):
                factors_dict_start[gw_start] = {}
                factors_dict_start[gw_start]["total_points_factor"] = 0
                factors_dict_start[gw_start]["ppg_factor"] = 0
                factors_dict_start[gw_start]["value_factor"] = 0
                factors_dict_start[gw_start]["bonus_factor"] = 0
                factors_dict_start[gw_start]["form_factor"] = 0
                factors_dict_start[gw_start]["fdr_factor"] = 1
                factors_dict_start[gw_start]["player_num"] = 1
                factors_dict_start[gw_start]["gw"] = gw_start
                factors_dict_start[gw_start]["last_date"] = "2023-08-17T14:00:00Z"
            with open("factors.json", "w") as data:
                json.dump(factors_dict_start, data, indent=4)
            with open("factors.json", "r") as data_file:
                factors = json.load(data_file)

        for gw in factors.keys():
            player_id_list = self.player_data["id_x"].tolist()
            player_id_list.sort()
            try:
                player_check = fplapi.fpl_player_history(1, int(gw))
            except IndexError:
                player_check = fplapi.fpl_player_history(100, int(gw))
            except KeyError:
                return None
            player_check_date = datetime.strptime(player_check["date"], "%Y-%m-%dT%H:%M:%SZ")
            factors_check_date = datetime.strptime(factors[gw]["last_date"], "%Y-%m-%dT%H:%M:%SZ")
            if (
                player_check_date <= factors_check_date
            ):
                continue

            new_total_points_factor = factors[gw]["total_points_factor"]
            new_ppg_factor = factors[gw]["ppg_factor"]
            new_value_factor = factors[gw]["value_factor"]
            new_bonus_factor = factors[gw]["bonus_factor"]
            new_form_factor = factors[gw]["form_factor"]
            new_fdr_factor = factors[gw]["fdr_factor"]
            new_player_num = factors[gw]["player_num"]

            print(f"{gw}/{MAX_GW_NUMBER}")
            for player_id in player_id_list:
                print(f"{player_id}/{len(player_id_list)}")
                try:
                    player_history_data = fplapi.fpl_player_history(int(player_id), int(gw))
                except IndexError:
                    continue

                if (
                    player_history_data["total_points"] <= 0
                    or player_history_data["ppg"] <= 0
                    or player_history_data["value_season"] <= 0
                    or player_history_data["bonus"] <= 0
                    or player_history_data["form"] <= 0
                ):
                    continue
                else:
                    total_points_factor = player_history_data["gw_points"] / player_history_data["total_points"]
                    ppg_factor = player_history_data["gw_points"] / player_history_data["ppg"]
                    value_factor = player_history_data["gw_points"] / player_history_data["value_season"]
                    bonus_factor = player_history_data["gw_points"] / player_history_data["bonus"]
                    form_factor = player_history_data["gw_points"] / player_history_data["form"]

                team = self.player_data[self.player_data["id_x"] == player_id]["team"].tolist()[0]
                fdr = self.fdr_data[self.fdr_data["team"] == team][f"gw{gw}"].tolist()[0]
                if np.isnan(fdr) or player_history_data["gw_points"] == 0:
                    continue
                else:
                    fdr_factor = player_history_data["gw_points"] / fdr

                if new_player_num == 1:
                    new_total_points_factor = total_points_factor
                    new_ppg_factor = ppg_factor
                    new_value_factor = value_factor
                    new_bonus_factor = bonus_factor
                    new_form_factor = form_factor
                    new_fdr_factor = fdr_factor
                else:
                    new_total_points_factor += (
                        total_points_factor
                        * (
                           factors[gw]["player_num"]
                           * total_points_factor
                           - factors[gw]["total_points_factor"]
                        )
                        / (
                           total_points_factor
                           * factors[gw]["player_num"]
                           * (factors[gw]["player_num"] + 1)
                        )

                    )
                    new_ppg_factor += (
                            ppg_factor
                            * (
                               factors[gw]["player_num"]
                               * ppg_factor
                               - factors[gw]["ppg_factor"]
                            )
                            / (
                               ppg_factor
                               * factors[gw]["player_num"]
                               * (factors[gw]["player_num"] + 1)
                            )

                    )
                    new_value_factor += (
                            value_factor
                            * (
                               factors[gw]["player_num"]
                               * value_factor
                               - factors[gw]["value_factor"]
                            )
                            / (
                               value_factor
                               * factors[gw]["player_num"]
                               * (factors[gw]["player_num"] + 1)
                            )

                    )
                    new_bonus_factor += (
                            bonus_factor
                            * (
                               factors[gw]["player_num"]
                               * bonus_factor
                               - factors[gw]["bonus_factor"]
                            )
                            / (
                               bonus_factor
                               * factors[gw]["player_num"]
                               * (factors[gw]["player_num"] + 1)
                            )

                    )
                    new_form_factor += (
                            form_factor
                            * (
                               factors[gw]["player_num"]
                               * form_factor
                               - factors[gw]["form_factor"]
                            )
                            / (
                               form_factor
                               * factors[gw]["player_num"]
                               * (factors[gw]["player_num"] + 1)
                            )

                    )
                    new_fdr_factor += (
                            fdr_factor
                            * (
                               factors[gw]["player_num"]
                               * fdr_factor
                               - factors[gw]["fdr_factor"]
                            )
                            / (
                               fdr_factor
                               * factors[gw]["player_num"]
                               * (factors[gw]["player_num"] + 1)
                            )

                    )
                new_player_num += 1
                new_last_date = player_history_data["date"]
                check_new_last_date = datetime.strptime(player_history_data["date"], "%Y-%m-%dT%H:%M:%SZ")

                factors[gw]["total_points_factor"] = new_total_points_factor
                factors[gw]["ppg_factor"] = new_ppg_factor
                factors[gw]["value_factor"] = new_value_factor
                factors[gw]["bonus_factor"] = new_bonus_factor
                factors[gw]["form_factor"] = new_form_factor
                factors[gw]["fdr_factor"] = new_fdr_factor
                factors[gw]["player_num"] = new_player_num
                factors[gw]["gw"] = int(gw)
                if check_new_last_date >= datetime.strptime(factors[gw]["last_date"], "%Y-%m-%dT%H:%M:%SZ"):
                    factors[gw]["last_date"] = new_last_date

            with open("factors.json", "w") as data:
                json.dump(factors, data, indent=4)

    def point_calculation(self, first_gw_number: int, last_gw_number: int) -> None:
        """
        Calculates the basic points for player comparison

        :param first_gw_number: An integer of the input of the first GW
        :type first_gw_number: int
        :param last_gw_number: An integer of the input of the last GW
        :type last_gw_number: int
        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        factors_average = {
            "total_points_factor": 0,
            "ppg_factor": 0,
            "value_factor": 0,
            "bonus_factor": 0,
            "form_factor": 0,
            "fdr_factor": 0,
        }

        for gw in range(first_gw_number, last_gw_number + 1):
            factors_average["total_points_factor"] += factors[str(gw)]["total_points_factor"] / 10
            factors_average["ppg_factor"] += factors[str(gw)]["ppg_factor"] / 10
            factors_average["value_factor"] += factors[str(gw)]["value_factor"] / 10
            factors_average["bonus_factor"] += factors[str(gw)]["bonus_factor"] / 10
            factors_average["form_factor"] += factors[str(gw)]["form_factor"] / 10
            factors_average["fdr_factor"] += factors[str(gw)]["fdr_factor"] / 10

        self.player_data["point_calculation"] = (
                self.player_data["total_points"]
                ** factors_average["total_points_factor"]
                * self.player_data["value_season"].astype(float)
                ** factors_average["value_factor"]
                * self.player_data["points_per_game"].astype(float)
                ** factors_average["ppg_factor"]
                * self.player_data["form_new"].astype(float)
                ** factors_average["form_factor"]
                * self.player_data["bonus_new"]
                ** factors_average["bonus_factor"]
                / (
                   self.player_data["fdr_final"]
                   ** factors_average["fdr_factor"]
                )
        )

        self.player_data["point_calculation"] = (
                self.player_data["point_calculation"]
                * 100
                / (max(self.player_data["point_calculation"]) + 1)
        )

    def captain_points(self, first_gw_number: int, last_gw_number: int) -> None:
        """
        Calculates the captaincy points

        :param first_gw_number: An integer of the input of the first GW
        :type first_gw_number: int
        :param last_gw_number: An integer of the input of the last GW
        :type last_gw_number: int
        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        factors_average = {
            "total_points_factor": 0,
            "ppg_factor": 0,
            "value_factor": 0,
            "bonus_factor": 0,
            "form_factor": 0,
            "fdr_factor": 0,
        }

        for gw in range(first_gw_number, last_gw_number + 1):
            factors_average["total_points_factor"] += factors[str(gw)]["total_points_factor"] / 10
            factors_average["ppg_factor"] += factors[str(gw)]["ppg_factor"] / 10
            factors_average["value_factor"] += factors[str(gw)]["value_factor"] / 10
            factors_average["bonus_factor"] += factors[str(gw)]["bonus_factor"] / 10
            factors_average["form_factor"] += factors[str(gw)]["form_factor"] / 10
            factors_average["fdr_factor"] += factors[str(gw)]["fdr_factor"] / 10

        self.player_data["captain_points"] = (
                self.player_data["total_points"]
                ** (2 * factors_average["total_points_factor"])
                * self.player_data["points_per_game"].astype(float)
                ** factors_average["ppg_factor"]
                * self.player_data["form_new"].astype(float)
                ** factors_average["form_factor"]
                * self.player_data["bonus_new"]
                ** factors_average["bonus_factor"]
                / (
                   self.player_data["fdr_final"]
                   ** factors_average["fdr_factor"]
                )
        )

        self.player_data["captain_points"] = (
                self.player_data["captain_points"]
                * 100
                / (max(self.player_data["captain_points"]) + 1)
        )

    def transfer_points(self, gw_number: int, first_gw_number: int, last_gw_number: int) -> None:
        """
        Calculates the transfer points

        :param gw_number: An integer of the number of GWs played
        :type gw_number: int
        :param first_gw_number: An integer of the input of the first GW
        :type first_gw_number: int
        :param last_gw_number: An integer of the input of the last GW
        :type last_gw_number: int
        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        factors_average = {
            "total_points_factor": 0,
            "ppg_factor": 0,
            "value_factor": 0,
            "bonus_factor": 0,
            "form_factor": 0,
            "fdr_factor": 0,
        }

        for gw in range(first_gw_number, last_gw_number + 1):
            factors_average["total_points_factor"] += factors[str(gw)]["total_points_factor"] / 10
            factors_average["ppg_factor"] += factors[str(gw)]["ppg_factor"] / 10
            factors_average["value_factor"] += factors[str(gw)]["value_factor"] / 10
            factors_average["bonus_factor"] += factors[str(gw)]["bonus_factor"] / 10
            factors_average["form_factor"] += factors[str(gw)]["form_factor"] / 10
            factors_average["fdr_factor"] += factors[str(gw)]["fdr_factor"] / 10

        self.player_data["transfer_points"] = (
                np.abs(self.player_data["total_points"] - 4)
                ** (
                    factors_average["total_points_factor"]
                    + factors_average["value_factor"]
                    + factors_average["ppg_factor"]
                )
                * self.player_data["bonus_new"]
                ** factors_average["bonus_factor"]
                * (
                   np.abs(self.player_data["form_new"].astype(float) - (4 / 5.0))
                   ** factors_average["form_factor"]
                )
                / (
                   self.player_data["cost"]
                   ** factors_average["value_factor"]
                   * self.player_data["fdr_final"]
                   ** factors_average["fdr_factor"]
                   * gw_number
                   ** factors_average["ppg_factor"]
                )
        )

        self.player_data["transfer_points"] = (
                self.player_data["transfer_points"]
                * 100
                / (max(self.player_data["transfer_points"]) + 1)
        )

    def manager_points(self, first_gw_number: int, last_gw_number: int) -> None:
        """
        Calculates points for manager comparison

        :param first_gw_number: An integer of the input of the first GW
        :type first_gw_number: int
        :param last_gw_number: An integer of the input of the last GW
        :type last_gw_number: int
        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        factors_average = {
            "total_points_factor": 0,
            "ppg_factor": 0,
            "value_factor": 0,
            "bonus_factor": 0,
            "form_factor": 0,
            "fdr_factor": 0,
        }

        for gw in range(first_gw_number, last_gw_number + 1):
            factors_average["total_points_factor"] += factors[str(gw)]["total_points_factor"] / 10
            factors_average["ppg_factor"] += factors[str(gw)]["ppg_factor"] / 10
            factors_average["value_factor"] += factors[str(gw)]["value_factor"] / 10
            factors_average["bonus_factor"] += factors[str(gw)]["bonus_factor"] / 10
            factors_average["form_factor"] += factors[str(gw)]["form_factor"] / 10
            factors_average["fdr_factor"] += factors[str(gw)]["fdr_factor"] / 10

        self.player_data["manager_points"] = (
            self.player_data["total_points"]
            ** (3 * factors_average["total_points_factor"])
            * self.player_data["form_new"].astype(float)
            ** factors_average["form_factor"]
            / (
                self.player_data["fdr_final"]
                ** factors_average["fdr_factor"]
            )
        )

        self.player_data["manager_points"] = (
                self.player_data["manager_points"]
                * 100
                / (max(self.player_data["manager_points"]) + 1)
        )


def fdr_input() -> list:
    """
    Requests an input of the GW period for the calculations

    :return: A list of the first and last GW from the input
    """
    first_gw_number = 9999
    last_gw_number = 9999

    while last_gw_number > MAX_GW_NUMBER or first_gw_number < MIN_GW_NUMBER or first_gw_number > last_gw_number:
        first_gw_number = 9999
        last_gw_number = 9999
        try:
            print("\nThe program needs to calculate points based on the players' stats and upcoming games."
                  "\nPlease enter the GW period for which you want the points to be calculated.")
            first_gw_number = int(input("\nFirst GW: "))
            last_gw_number = int(input("Last GW: "))
        except ValueError:
            print("\nInvalid GW numbers.")
        else:
            if (
                last_gw_number > MAX_GW_NUMBER or first_gw_number < MIN_GW_NUMBER
                or first_gw_number > last_gw_number
            ):
                print("\nInvalid GW numbers.")
    return [first_gw_number, last_gw_number]


def calculate_fdr(first_gw_number: int, last_gw_number: int) -> list:
    """
    Calculates the FDR based on the user's input

    :param first_gw_number: An integer of the input of the first GW
    :type first_gw_number: int
    :param last_gw_number: An integer of the input of the last GW
    :type last_gw_number: int
    :return: A list of the GWs that are going to be included in the calculations
    """
    fdr_gw = []
    for gw in range(first_gw_number, last_gw_number + 1):
        fdr_gw.append(f"gw{gw}")
    return fdr_gw


# if __name__ == "__main__":
    # fpl = FPLstats("username", "password")
    # fpl.calculate_points()
    # print(fpl.fdr_data["gw29"][fpl.fdr_data.index[fpl.fdr_data["team"] == "ARS"].tolist()[0]])
    # print(fpl.player_stat("Johnson", "total_points"))
    # print(fpl.fdr_data)

    # gw = 33
    # team = fpl.player_data[fpl.player_data["id_x"] == 17]["team"].tolist()[0]
    # fdr = fpl.fdr_data[fpl.fdr_data["team"] == team][f"gw{gw}"].tolist()[0]
    # if np.isnan(fdr):
    #     print("nope")
    # else:
    #     print("yep")

    # fpl.calculation_factors()
