import numpy as np
from functools import cache

import fplapi
from fplapi import FPLapi
import json

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
    def __init__(self):
        # Getting the Dataframes
        self.fplapi = FPLapi()
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
        # Calculating factor points
        # self.factor_point_calculation()
        self.calculation_factors()
        # Calculating points for player comparison
        self.point_calculation()
        # Calculating points for captaincy comparison
        self.captain_points()
        # Calculating points for transfer comparison
        self.transfer_points(self.last_gw_number)
        # Calculating points for manager comparison
        self.manager_points()

        self.player_data.sort_values(by=["point_calculation", "points_per_game"], ascending=False)

    @cache
    def player_stat(self, player_name: str, statistic_value: str):
        """
        Returns a specific player's stat

        :param player_name: Name of the player
        :type player_name: str
        :param statistic_value: Type of stat returned
        :type statistic_value: str
        :return: A specific stat for a specific player
        """
        return (
            self.player_data[statistic_value]
            [self.player_data.index[self.player_data["name"] == player_name].tolist()[0]]
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
            with open("factors.json", "w") as data:
                json.dump({}, data, indent=4)
            with open("factors.json", "r") as data_file:
                factors = json.load(data_file)

        factors_dict = {}
        for gw in factors.keys():
            player_check = fplapi.fpl_player_history(1, gw)
            if (
                player_check["date"] <= factors[gw]["last_date"]
            ):
                continue

            new_total_points_factor = factors[gw]["total_points_factor"]
            new_ppg_factor = factors[gw]["ppg_factor"]
            new_value_factor = factors[gw]["value_factor"]
            new_bonus_factor = factors[gw]["bonus_factor"]
            new_form_factor = factors[gw]["form_factor"]
            new_fdr_factor = factors[gw]["fdr_factor"]
            new_player_num = factors[gw]["player_num"]
            new_last_date = factors[gw]["last_date"]

            player_id_list = self.player_data["id_x"].tolist()
            print(f"{gw}/{MAX_GW_NUMBER}")
            for player_id in player_id_list:
                print(f"{player_id}/{len(player_id_list)}")
                player_history_data = fplapi.fpl_player_history(player_id, gw)

                total_points_factor = player_history_data["gw_points"] / player_history_data["total_points"]
                ppg_factor = player_history_data["gw_points"] / player_history_data["ppg"]
                value_factor = player_history_data["gw_points"] / player_history_data["value_season"]
                bonus_factor = player_history_data["gw_points"] / player_history_data["bonus"]
                form_factor = player_history_data["gw_points"] / player_history_data["form"]

                team = self.player_data[self.player_data["id_x"] == player_id]["team"].tolist()[0]
                fdr = self.fdr_data[self.fdr_data["team"] == team][f"gw{gw}"].tolist()[0]
                if np.isnan(fdr):
                    continue
                else:
                    fdr_factor = player_history_data["gw_points"] / fdr

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

                if player_history_data["date"] > new_last_date:
                    new_last_date = player_history_data["date"]

                factors_dict[gw]["total_points_factor"] = new_total_points_factor
                factors_dict[gw]["ppg_factor"] = new_ppg_factor
                factors_dict[gw]["value_factor"] = new_value_factor
                factors_dict[gw]["bonus_factor"] = new_bonus_factor
                factors_dict[gw]["form_factor"] = new_form_factor
                factors_dict[gw]["fdr_factor"] = new_fdr_factor
                factors_dict[gw]["player_num"] = new_player_num
                factors_dict[gw]["gw"] = gw
                factors_dict[gw]["last_date"] = new_last_date

                factors.update(factors_dict)
                with open("factors.json", "w") as data:
                    json.dump(factors_dict, data, indent=4)

    def point_calculation(self) -> None:
        """
        Calculates the basic points for player comparison

        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        self.player_data["point_calculation"] = (
                self.player_data["total_points"]
                * factors["total_points_factor"]
                * self.player_data["value_season"].astype(float)
                * factors["value_factor"]
                * self.player_data["points_per_game"].astype(float)
                * factors["points_per_game_factor"]
                * self.player_data["form"].astype(float)
                * factors["form_factor"]
                * self.player_data["bonus_new"]
                * factors["bonus_factor"]
                / (
                   self.player_data["fdr_final"]
                   * factors["fdr_factor"]
                   * factors["point_calculation_factor"]
                )
        )

    def captain_points(self) -> None:
        """
        Calculates the captaincy points

        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        self.player_data["captain_points"] = (
                self.player_data["total_points"] ** 2
                * factors["total_points_factor"] ** 2
                * self.player_data["points_per_game"].astype(float)
                * factors["points_per_game_factor"]
                * self.player_data["form"].astype(float)
                * factors["form_factor"]
                * self.player_data["bonus_new"]
                * factors["bonus_factor"]
                / (
                   self.player_data["fdr_final"]
                   * factors["fdr_factor"]
                   * factors["point_calculation_factor"]
                )
        )

    def transfer_points(self, gw_number: int) -> None:
        """
        Calculates the transfer points

        :param gw_number: An integer of the number of GWs played
        :type gw_number: int
        :return: None
        """
        with open("factors.json", "r") as file:
            factors = json.load(file)
        self.player_data["transfer_points"] = (
                np.abs(self.player_data["total_points"] - 4) ** 3
                * factors["total_points_factor"]
                * factors["value_factor"]
                * factors["points_per_game_factor"]
                * self.player_data["bonus_new"]
                * factors["bonus_factor"]
                * (
                   (self.player_data["form"].astype(float)
                    * factors["form_factor"])
                   - (4 / 5.0)
                )
                / (
                   self.player_data["cost"]
                   * self.player_data["fdr_final"]
                   * factors["fdr_factor"]
                   * factors["point_calculation_factor"]
                   * gw_number
                )
        )

    def manager_points(self) -> None:
        """
        Calculates points for manager comparison

        :return: None
        """
        self.player_data["manager_points"] = (
            self.player_data["total_points"] ** 3
            * self.player_data["form"].astype(float)
            / (
                self.player_data["fdr_final"]
            )
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


if __name__ == "__main__":
    fpl = FPLstats()
    fpl.calculate_points()
    # print(fpl.fdr_data["gw29"][fpl.fdr_data.index[fpl.fdr_data["team"] == "ARS"].tolist()[0]])
    # print(fpl.player_stat("Cunha", "factor_point_calculation"))
    # print(fpl.player_stat("Wissa", "factor_point_calculation"))
    print(fpl.fdr_data)

    # gw = 33
    # team = fpl.player_data[fpl.player_data["id_x"] == 17]["team"].tolist()[0]
    # fdr = fpl.fdr_data[fpl.fdr_data["team"] == team][f"gw{gw}"].tolist()[0]
    # if np.isnan(fdr):
    #     print("nope")
    # else:
    #     print("yep")
