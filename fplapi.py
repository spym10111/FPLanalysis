import requests
import numpy as np
import pandas as pd
from functools import cache

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
    def __init__(self):
        self.team_id = 0

        pd.set_option("display.max_columns", None)
        self.main_df = self.fpl_player_stats()
        self.fixtures_df = self.fpl_fdr()

    @cache
    def fpl_player_stats(self) -> pd.DataFrame:
        """
        Gets statistics on players from the official Fantasy Premier League site.

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
        Gets the FDR values from the official Fantasy Premier League site.

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
                    team_list.append(fixtures["team_a_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                    gw_count.append(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                elif (
                    fixtures["team_h"][fixtures.index[i == fixtures["id"]].tolist()[0]]
                    == teams["id"][teams.index[team == teams["short_name"]].tolist()[0]]
                    and pd.isna(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]]) is False
                ):
                    team_list.append(fixtures["team_h_difficulty"][fixtures.index[i == fixtures["id"]].tolist()[0]])
                    gw_count.append(fixtures["event"][fixtures.index[i == fixtures["id"]].tolist()[0]])
            data.append(team_list)
        self.fixtures_df = pd.DataFrame(data, columns=column_names)
        return self.fixtures_df

    @cache
    def get_team(self, username: str, password: str) -> dict:
        """
        Gets information from the player's team id.

        :param username: E-mail used for request on the FPL API
        :type username: str
        :param password: Password used for request on the FPL API
        :type password: str
        :return: A dictionary containing information on the user's FPL team
        """
        session = requests.session()
        url = "https://users.premierleague.com/accounts/login/"
        payload = {
            "password": password,
            "login": username,
            "redirect_uri": "https://fantasy.premierleague.com/a/login",
            "app": "plfpl-web"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            "accept-language": "en-US,en;q=0.5"
        }
        session.post(url, data=payload, headers=headers, verify=True)

        response = session.get("https://fantasy.premierleague.com/api/me/", verify=True)
        response.raise_for_status()
        response_json = response.json()
        self.team_id = response_json["player"]["entry"]

        response_team = session.get(f"https://fantasy.premierleague.com/api/my-team/{self.team_id}")
        response_team_json = response_team.json()
        picks = pd.json_normalize(response_team_json["picks"])
        transfers = pd.json_normalize(response_team_json["transfers"])

        element_prices = []
        for price in picks["selling_price"]:
            element_prices.append(price / 10)

        team_dict = {
            "total_budget": sum(picks["selling_price"]) / 10 + (transfers["bank"][0] / 10),
            "starters_budget": sum(picks["selling_price"]) / 10 - sum(picks["selling_price"][11:15]) / 10,
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


if __name__ == "__main__":
    print(FPLapi().fixtures_df)
