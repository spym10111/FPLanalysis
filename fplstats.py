import numpy as np
from functools import cache

import fplapi
from fplapi import FPLapi
from itertools import combinations
import json

MIN_GW_NUMBER = 1
MAX_GW_NUMBER = 38


class FPLstats:
    """
    Holds the methods for calculating the FPL statistics.

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
        np.set_printoptions(legacy="1.25")

    def calculate_points(self) -> None:
        """
        Calculates the stats that are taken into account when creating the team or searching for players. The results
        are stored in the players Dataframe created in the fplapi.py.

        :return: None
        """
        # Number of GWs to calculate
        fdr_range = fdr_input()
        fdr_gw = calculate_fdr(fdr_range[0], fdr_range[1])
        # Number of GWs the statistics correspond to
        gw_number = fplapi.gw_played()
        # Calculating the FDR part of the function
        self.fdr_product(fdr_gw)

        # The functions used for team selection
        self.player_data["bonus_new"] = self.player_data["bonus"] + 1
        # Calculating factor points
        self.factor_point_calculation()
        self.calculation_factors()
        # Calculating points for player comparison
        self.point_calculation()
        # Calculating points for captaincy comparison
        self.captain_points()
        # Calculating points for transfer comparison
        self.transfer_points(gw_number)
        # Calculating points for manager comparison
        self.manager_points()

        self.player_data.sort_values(by=["point_calculation", "points_per_game"], ascending=False)

    @cache
    def player_stat(self, player_name: str, statistic_value: str):
        """
        Returns a specific player's stat.

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
        Calculates the FDR part of the function.

        :param fdr_gw: A list of the GWs included in the calculations.
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
                        fdr_final = team_fdr[0]
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
        Used to calculate the point formula factors for every value. Creates a .json file with the values.

        :return: None
        """
        player_list = []
        for name in self.player_data["name"]:
            player_list.append(name)

        point_calculation_factor_list = []
        total_points_factor_list = []
        points_per_game_factor_list = []
        value_factor_list = []
        bonus_factor_list = []
        form_factor_list = []
        fdr_factor_list = []

        for duo in combinations(player_list, 2):
            if (
                self.player_stat(duo[0], "factor_point_calculation") != 0
                and self.player_stat(duo[1], "factor_point_calculation") != 0
            ):
                point_calculation_factor = (
                    float(self.player_stat(duo[0], "factor_point_calculation"))
                    / float(self.player_stat(duo[1], "factor_point_calculation"))
                )
                point_calculation_factor_list.append(point_calculation_factor)

                total_points_factor = (
                    float(self.player_stat(duo[0], "total_points"))
                    / float(self.player_stat(duo[1], "total_points"))
                )
                total_points_factor_list.append(total_points_factor)

                points_per_game_factor = (
                    float(self.player_stat(duo[0], "points_per_game"))
                    / float(self.player_stat(duo[1], "points_per_game"))
                )
                points_per_game_factor_list.append(points_per_game_factor)

                value_factor = (
                    float(self.player_stat(duo[0], "value_season"))
                    / float(self.player_stat(duo[1], "value_season"))
                )
                value_factor_list.append(value_factor)

                bonus_factor = (
                    float(self.player_stat(duo[0], "bonus_new"))
                    / float(self.player_stat(duo[1], "bonus_new"))
                )
                bonus_factor_list.append(bonus_factor)

                form_factor = (
                    float(self.player_stat(duo[0], "form"))
                    / float(self.player_stat(duo[1], "form"))
                )
                form_factor_list.append(form_factor)

                fdr_factor = (
                    float(self.player_stat(duo[0], "fdr_final"))
                    / float(self.player_stat(duo[1], "fdr_final"))
                )
                fdr_factor_list.append(fdr_factor)
        avg_point_calculation_factor = abs(np.average(point_calculation_factor_list))
        avg_total_points_factor = abs(np.average(total_points_factor_list))
        avg_points_per_game_factor = abs(np.average(points_per_game_factor_list))
        avg_value_factor = abs(np.average(value_factor_list))
        avg_bonus_factor = abs(np.average(bonus_factor_list))
        avg_form_factor = abs(np.average(form_factor_list))
        avg_fdr_factor = abs(np.average(fdr_factor_list))
        factor_dict = {
            "point_calculation_factor": avg_point_calculation_factor,
            "total_points_factor": avg_total_points_factor,
            "points_per_game_factor": avg_points_per_game_factor,
            "value_factor": avg_value_factor,
            "bonus_factor": avg_bonus_factor,
            "form_factor": avg_form_factor,
            "fdr_factor": avg_fdr_factor,
        }
        with open("factors.json", "w") as file:
            json.dump(factor_dict, file, indent=4)

    def factor_point_calculation(self) -> None:
        """
        Calculates the factor points.

        :return: None
        """
        self.player_data["factor_point_calculation"] = (
                self.player_data["total_points"].astype(float)
                * self.player_data["value_season"].astype(float)
                * self.player_data["points_per_game"].astype(float)
                * self.player_data["form"].astype(float)
                * self.player_data["bonus_new"].astype(float)
                / self.player_data["fdr_final"].astype(float)
        )

    def point_calculation(self) -> None:
        """
        Calculates the basic points for player comparison.

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
        Calculates the captaincy points.

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
        Calculates the transfer points.

        :param gw_number: An integer of the number of GWs played.
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
        Calculates points for manager comparison.

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
    Requests an input of the GW period for the calculations.

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
    Calculates the FDR based on the user's input.

    :param first_gw_number: An integer of the input of the first GW
    :type first_gw_number: int
    :param last_gw_number: An integer of the input of the last GW
    :type last_gw_number: int
    :return: A list of the GWs that are going to be included in the calculations.
    """
    fdr_gw = []
    for gw in range(first_gw_number, last_gw_number + 1):
        fdr_gw.append(f"gw{gw}")
    return fdr_gw


if __name__ == "__main__":
    fpl = FPLstats()
    fpl.calculate_points()
    # print(fpl.fdr_data["gw29"][fpl.fdr_data.index[fpl.fdr_data["team"] == "ARS"].tolist()[0]])
    print(fpl.fdr_data)
