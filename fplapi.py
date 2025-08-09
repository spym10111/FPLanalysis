import requests
import numpy as np
import pandas as pd
from functools import cache
from apilogin import Login

TOTAL_GW_NUMBER = 38


class FPLapi:
    """
    Holds methods that return fantasy statistics on players from the official Premier League source:
    www.premierleague.com

    Attributes:
        main_df: The main dataframe with all the player stats
        fixtures_df: The dataframe containing the info on the FDR per team
        team_id: The teams id we get after entering the log-in information
    """
    def __init__(self, username, password):
        self.apilogin = Login(username, password)
        self.team_id = self.apilogin.team_id

        pd.set_option("display.max_columns", None)
        self.main_df = self.fpl_player_stats()
        self.fixtures_df = self.fpl_fdr()

    @cache
    def fpl_player_stats(self) -> pd.DataFrame:
        """
        Gets statistics on players from the official Fantasy Premier League site

        :return: A dataframe containing players' FPL information
        """
        # Requesting data from www.premierleague.com and transforming into usable Dataframe
        base_url = "https://fantasy.premierleague.com/api/"
        r = requests.get(f"{base_url}bootstrap-static/", verify=True).json()

        players = pd.json_normalize(r["elements"])
        teams = pd.json_normalize(r["teams"])
        positions = pd.json_normalize(r["element_types"])

        players = players.rename(columns={"team": "team_id"})
        teams_df = teams[["id", "short_name"]]
        self.main_df = pd.merge(
            left=players,
            right=teams_df,
            left_on='team_id',
            right_on='id'
        )
        positions_df = positions[["id", "singular_name_short"]]
        self.main_df = self.main_df.merge(
            positions_df,
            left_on='element_type',
            right_on='id'
        )

        self.main_df = self.main_df.rename(columns={"web_name": "name", "short_name": "team",
                                                    "singular_name_short": "position", "now_cost": "cost"})
        self.main_df["cost"] = self.main_df["cost"] / 10.0
        return self.main_df

    @cache
    def fpl_fdr(self) -> pd.DataFrame:
        """
        Gets the FDR values from the official Fantasy Premier League site

        :return: A dataframe containing FDR information
        """
        np.set_printoptions(legacy="1.25")
        base_url = "https://fantasy.premierleague.com/api/"
        r = requests.get(f"{base_url}fixtures", verify=True).json()
        r_2 = requests.get(f"{base_url}bootstrap-static/", verify=True).json()

        fixtures = pd.json_normalize(r)
        teams = pd.json_normalize(r_2["teams"])

        column_names = ["team"]
        for i in range(TOTAL_GW_NUMBER):
            column_names.append(f"gw{i+1}")

        data = []
        for team in teams["short_name"]:
            team_list = [team]
            gw_count = []
            for i in fixtures["id"]:
                if (
                    fixtures["team_a"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    == teams["id"][teams.index[team == teams["short_name"]].tolist()[0]]
                    and pd.isna(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]]) is False
                ):
                    if fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]] in gw_count:
                        extra_game_fdr = fixtures["team_a_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                        team_list[-1] = team_list[-1] * extra_game_fdr / (team_list[-1] + extra_game_fdr)
                    else:
                        team_list.append(fixtures["team_a_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                        gw_count.append(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                elif (
                    fixtures["team_h"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    == teams["id"][teams.index[team == teams["short_name"]].tolist()[0]]
                    and pd.isna(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]]) is False
                ):
                    if fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]] in gw_count:
                        extra_game_fdr = fixtures["team_h_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                        team_list[-1] = team_list[-1] * extra_game_fdr / (team_list[-1] + extra_game_fdr)
                    else:
                        team_list.append(fixtures["team_h_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                        gw_count.append(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
            for n in range(1, 39):
                if n not in gw_count:
                    team_list.insert(n, np.nan)
                    gw_count.insert(n - 1, n)
                    # Temporary comment of code that might be useful in future bug (predictions were made...)
                    # for i in fixtures["id"]:
                    #     if (
                    #         fixtures["team_a"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    #         == teams["id"][teams.index[team == teams["short_name"]].tolist()[0]]
                    #         and pd.isna(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                    #     ):
                    #         team_list.pop(n)
                    #         team_list.insert(
                    #             n, fixtures["team_a_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    #         )
                    #     elif (
                    #           fixtures["team_h"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    #           == teams["id"][teams.index[team == teams["short_name"]].tolist()[0]]
                    #           and pd.isna(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                    #     ):
                    #         team_list.pop(n)
                    #         team_list.insert(
                    #             n, fixtures["team_h_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    #         )
            data.append(team_list)
        self.fixtures_df = pd.DataFrame(data, columns=column_names)
        return self.fixtures_df

    @cache
    def get_team(self, username, password) -> dict:
        """
        Gets information from the player's team id

        :return: A dictionary containing information on the user's FPL team
        """
        session = requests.Session()

        response_team = session.get(
            f"https://fantasy.premierleague.com/api/my-team/{self.team_id}",
            headers={
                "X-API-Authorization": f"Bearer {FPLapi(username, password).apilogin.access_token}",
            }
        )
        response_team_json = response_team.json()
        picks = pd.json_normalize(response_team_json["picks"])
        transfers = pd.json_normalize(response_team_json["transfers"])

        element_prices = []
        for price in picks["selling_price"]:
            element_prices.append(price / 10)

        team_dict = {
            "total_budget": picks["selling_price"].sum() / 10 + (transfers["bank"][0] / 10),
            "starters_budget": picks["selling_price"].sum() / 10 - picks["selling_price"][11:15].sum() / 10,
            "changes_budget": sum([picks["selling_price"][11], picks["selling_price"][12], picks["selling_price"][13],
                                   picks["selling_price"][14]]) / 10,
            "bank_budget": transfers["bank"][0] / 10,
            "team_elements": [element for element in picks["element"]],
            "starters_prices": [price for price in element_prices[0:11]],
            "changes_prices": [price for price in element_prices[11:15]]
        }
        # Changing the player cost in the main_df based on the selling price we get from the API
        # The functionality of changing the main_df here is based on the fact that the info of the main_df is stored in
        # the cache and the fpl_player_stats function just calls the result from there without running again
        # (a bit of cheating someone might say... *sips tea sardonically*)
        for element in team_dict["team_elements"]:
            self.main_df.loc[self.main_df.index[self.main_df["id_x"] == element], ["cost"]] = (
                element_prices[team_dict["team_elements"].index(element)]
            )
        return team_dict


@cache
def fpl_player_history(player_id: int, fixture: int) -> dict:
    """
    Gets data from previous Gameweeks for a player

    :param player_id: The player's ID on the FPL API
    :type player_id: int
    :param fixture: The Gameweek up to which the values are calculated
    :type fixture: int
    :return: A dictionary of values used for factor point calculation
    """
    pd.set_option("display.max_columns", None)
    np.set_printoptions(legacy="1.25")

    base_url = "https://fantasy.premierleague.com/api/"
    r = requests.get(f"{base_url}element-summary/{player_id}", verify=True).json()
    history = pd.json_normalize(r["history"])

    date = history[history["round"] == fixture]["kickoff_time"].tolist()[0]
    gw = history[history["round"] == fixture]["round"].tolist()[0]
    fixture_points = history[history["round"] == fixture]["total_points"].sum()
    total_points = history[history["round"] <= fixture]["total_points"].sum()
    points_per_game = total_points / fixture
    form = 0
    if fixture <= 5:
        form = total_points / fixture
    elif fixture > 5:
        form_points = history[(history["round"] <= fixture)
                              & (history["round"] > fixture - 5)]["total_points"].sum()
        form = form_points / 5
    cost = history[history["round"] == fixture]["value"].tolist()[0] / 10
    value_season = total_points / cost
    bonus = history[history["round"] <= fixture]["bonus"].sum() + fixture

    player_history_stats = {
        "id": history["element"][0],
        "date": date,
        "gw": gw,
        "gw_points": fixture_points,
        "total_points": round(total_points, 1),
        "ppg": round(points_per_game, 1),
        "form": round(form, 1),
        "value_season": round(value_season, 1),
        "bonus": round(bonus, 1),
    }

    return player_history_stats


def check_status(username: str, password: str) -> None:
    """
    Checks if the username and password provided correspond to an actual FPL account

    :param username: E-mail used for request on the FPL API
    :type username: str
    :param password: Password used for request on the FPL API
    :type password: str
    :return: None
    """
    session = requests.Session()

    response_team = session.get(
        f"https://fantasy.premierleague.com/api/my-team/{FPLapi(username, password).team_id}",
        headers={
            "X-API-Authorization": f"Bearer {FPLapi(username, password).apilogin.access_token}",
        }
    )
    response_team.raise_for_status()


@cache
def gw_played() -> int:
    """
    Returns the last Gameweek played

    :return: An integer of the last Gameweek played
    """
    base_url = "https://fantasy.premierleague.com/api/"
    r = requests.get(f"{base_url}bootstrap-static/", verify=True).json()

    events = pd.json_normalize(r["events"])

    last_gw = 0
    for n in events["id"]:
        if events["finished"].tolist()[n-1]:
            last_gw = n
    if last_gw == 0:
        last_gw = 1
    return last_gw


# if __name__ == "__main__":
    # print(fpl_player_history(17, 33))
    # print(FPLapi(username, password).fpl_player_stats())
    # print(FPLapi(username, password).fpl_fdr())
    # print(gw_played())
