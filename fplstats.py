import numpy as np
from functools import reduce, cache
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

    def calculate_points(self):
        """
        Calculates the stats that are taken into account when creating the team or searching for players.
        """
        # Number of GWs to calculate
        fdr_gw = []
        first_gw_number = 9999
        last_gw_number = 9999

        while last_gw_number > MAX_GW_NUMBER or first_gw_number < MIN_GW_NUMBER or first_gw_number > last_gw_number:
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
        for gw in range(first_gw_number, last_gw_number + 1):
            fdr_gw.append(f"gw{gw}")

        # Number of GWs the statistics correspond to
        gw_number = 0
        while gw_number < 1 or gw_number > MAX_GW_NUMBER:
            try:
                gw_number = int(input("\nPlease enter the last GW played: "))
            except ValueError:
                print("\nInvalid GW number.")
            else:
                if gw_number < 1 or gw_number > MAX_GW_NUMBER:
                    print("\nInvalid GW number.")

        # Calculating the FDR part of the function
        fdr_index = []
        for player_team in self.player_data["team"]:
            fdr_index.append(self.fdr_data.index[self.fdr_data["team"] == player_team].tolist()[0])

        # Calculating FDR as a product
        mult = []
        for gw in fdr_gw:
            mult.append(self.fdr_data[gw].tolist())
        self.fdr_data["mult"] = reduce(np.multiply, mult)
        self.player_data["fdr_mult"] = ""
        fdr_mult_list = self.player_data["fdr_mult"].to_list()
        for i in range(len(fdr_mult_list)):
            fdr_mult_list[i] = self.fdr_data["mult"].to_list()[fdr_index[i]]
        self.player_data["fdr_mult"] = fdr_mult_list

        # The functions used for team selection
        self.player_data["bonus_new"] = self.player_data["bonus"] + 1

        # Calculating points for factor creation
        self.player_data["factor_point_calculation"] = (
                self.player_data["total_points"]
                * self.player_data["value_season"].astype(float)
                * self.player_data["points_per_game"].astype(float)
                * self.player_data["form"].astype(float)
                * self.player_data["bonus_new"]
                / self.player_data["fdr_mult"]
        )

        self.calculation_factors()

        # Calculating points for player comparison
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
                    self.player_data["fdr_mult"]
                    * factors["fdr_factor"]
                    * factors["point_calculation_factor"]
                )
        )

        # Calculating points for captaincy comparison
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
                    self.player_data["fdr_mult"]
                    * factors["fdr_factor"]
                    * factors["point_calculation_factor"]
                )
        )

        # Calculating points for transfer comparison
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
                   * self.player_data["fdr_mult"]
                   * factors["fdr_factor"]
                   * factors["point_calculation_factor"]
                   * gw_number
                )
        )

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

    def calculation_factors(self):
        """
        Used to calculate the point formula factors for every value.
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
                    self.player_stat(duo[0], "factor_point_calculation")
                    / self.player_stat(duo[1], "factor_point_calculation")
                )
                point_calculation_factor_list.append(point_calculation_factor)

                total_points_factor = (
                    self.player_stat(duo[0], "total_points")
                    / self.player_stat(duo[1], "total_points")
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
                    self.player_stat(duo[0], "bonus_new")
                    / self.player_stat(duo[1], "bonus_new")
                )
                bonus_factor_list.append(bonus_factor)

                form_factor = (
                    float(self.player_stat(duo[0], "form"))
                    / float(self.player_stat(duo[1], "form"))
                )
                form_factor_list.append(form_factor)

                fdr_factor = (
                    self.player_stat(duo[0], "fdr_mult")
                    / self.player_stat(duo[1], "fdr_mult")
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


if __name__ == "__main__":
    print(FPLstats().player_stat("Robinson", "id_x"))
