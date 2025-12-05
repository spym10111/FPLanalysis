import requests
import re
import secrets
import hashlib
import base64
import uuid


URL = {
        "auth": "https://account.premierleague.com/as/authorize",
        "start": "https://account.premierleague.com/davinci/policy/262ce4b01d19dd9d385d26bddb4297b6/start",
        "login": "https://account.premierleague.com/davinci/connections/867ed4363b2bc21c860085ad2baa817d/"
                 "capabilities/customHTMLTemplate",
        "resume": "https://account.premierleague.com/as/resume",
        "token": "https://account.premierleague.com/as/token",
}


def generate_code_verifier():
    return secrets.token_urlsafe(64)[:128]


def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


class Login:
    """
    Used to log into the Fantasy Premier League API.

    Attributes:
        username: E-mail used for logging in
        password: Password used for logging in
        team_id: Player's team ID
        access_token: Token needed to access API elements
    """
    def __init__(self, username, password):
        self.username = ""
        self.password = ""
        self.team_id = 0
        self.access_token = ""

        print("Authentication: ", end="")
        code_verifier = generate_code_verifier()  # code_verifier for PKCE
        code_challenge = generate_code_challenge(code_verifier)  # code_challenge from the code_verifier
        initial_state = uuid.uuid4().hex  # random initial state for the OAuth flow

        session = requests.Session()

        # Authorization
        payload_auth = {
            "client_id": "bfcbaf69-aade-4c1b-8f00-c1cb8a193030",
            "redirect_uri": "https://fantasy.premierleague.com/",
            "response_type": "code",
            "scope": "openid profile email offline_access",
            "state": initial_state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth = requests.post(URL["auth"], data=payload_auth)
        auth.raise_for_status()
        auth_html = auth.text

        access_token = re.search(r'"accessToken":"([^"]+)"', auth_html).group(1)
        # new state used for resume post request later
        new_state = re.search(r'<input[^>]+name="state"[^>]+value="([^"]+)"', auth_html).group(1)
        print("done")

        # Start
        print("Starting...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        response = session.post(URL["start"], headers=headers)
        response.raise_for_status()
        response_json = response.json()
        interaction_id = response_json["interactionId"]

        # Login
        print("Login: ", end="")
        response = session.post(
            URL["login"],
            headers={
                "interactionId": interaction_id,
            },
            json={
                "id": response_json["id"],
                "eventName": "continue",
                "parameters": {"eventType": "polling"},
                "pollProps": {"status": "continue", "delayInMs": 10, "retriesAllowed": 1, "pollChallengeStatus": False},
            },
        )
        response.raise_for_status()

        response = session.post(
            URL["login"],
            headers={
                "interactionId": interaction_id,
            },
            json={
                "id": response.json()["id"],
                "nextEvent": {
                    "constructType": "skEvent",
                    "eventName": "continue",
                    "params": [],
                    "eventType": "post",
                    "postProcess": {},
                },
                "parameters": {
                    "buttonType": "form-submit",
                    "buttonValue": "SIGNON",
                    "username": username,
                    "password": password,
                },
                "eventName": "continue",
            },
        )
        response.raise_for_status()
        response_json = response.json()

        response = session.post(
            f"https://account.premierleague.com/davinci/connections/{response_json['connectionId']}/"
            f"capabilities/customHTMLTemplate",  # need to use new connectionId from prev response
            headers=headers,
            json={
                "id": response_json["id"],
                "nextEvent": {
                    "constructType": "skEvent",
                    "eventName": "continue",
                    "params": [],
                    "eventType": "post",
                    "postProcess": {},
                },
                "parameters": {
                    "buttonType": "form-submit",
                    "buttonValue": "SIGNON",
                },
                "eventName": "continue",
            },
        )
        dv_response = response.json()["dvResponse"]

        # Resume
        response = session.post(
            URL["resume"],
            data={
                "dvResponse": dv_response,
                "state": new_state,
            },
            allow_redirects=False,
        )
        response.raise_for_status()

        location = response.headers["Location"]
        auth_code = re.search(r"[?&]code=([^&]+)", location).group(1)
        print("done")

        # Enter
        print("Accessing...")
        response = session.post(
            URL["token"],
            data={
                "grant_type": "authorization_code",
                "redirect_uri": "https://fantasy.premierleague.com/",
                "code": auth_code,
                "code_verifier": code_verifier,
                "client_id": "bfcbaf69-aade-4c1b-8f00-c1cb8a193030",
            },
        )
        response.raise_for_status()

        self.access_token = response.json()["access_token"]
        response = session.get(
            "https://fantasy.premierleague.com/api/me/",
            headers={"X-API-Authorization": f"Bearer {self.access_token}"})
        response.raise_for_status()

        self.team_id = response.json()["player"]["entry"]


# if __name__ == "__main__":
    # print(Login(username, password).response_team.json()["picks"])
