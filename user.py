import os
from utils import check_if_folder_exists
from requests import get
import json


class User:
    def __init__(self, riot_id: dict, api_key: str, **kwargs) -> None:
        """
        Initializes a User object with Riot ID and API key.

        Args:
            riot_id (dict): A dictionary containing Riot ID information, including
                            summoner's name, tag, and their encoded versions.
            api_key (str): API key required for accessing Riot API.

        Attributes:
            summoners_name (str): Summoner's name.
            summoners_tag (str): Summoner's tag.
            encoded_summoners_name (str): Encoded summoner's name.
            encoded_summoners_tag (str): Encoded summoner's tag.
            puuid (str): Player Universally Unique Identifier retrieved using the Riot API.
            solo_duo_matchs_list (list): List of solo/duo matches.
            flex_matchs_list (list): List of flex matches.

        Note:
            This method also fetches the player's PUUID and initializes match lists
            for solo/duo and flex queues using the provided API key.
        """
        self.summoners_name = riot_id["summoners_name"]
        self.summoners_tag = riot_id["summoners_tag"]
        self.encoded_summoners_name = riot_id["encoded_summoners_name"]
        self.encoded_summoners_tag = riot_id["encoded_summoners_tag"]
        self.puuid = (
            self.get_puuid(api_key=api_key)
            if "puuid" not in kwargs
            else kwargs["puuid"]
        )
        self.solo_duo_matchs_list = (
            self.list_matchs(matchs_list=[], start_index=0, api_key=api_key, queue=420)
            if "solo_duo_matchs_list" not in kwargs
            else kwargs["solo_duo_matchs_list"]
        )
        self.flex_matchs_list = (
            self.list_matchs(matchs_list=[], start_index=0, api_key=api_key, queue=440)
            if "flex_matchs_list" not in kwargs
            else kwargs["flex_matchs_list"]
        )

    @classmethod
    def load_from_json(cls, file_path: str, api_key: str):
        """
        Creates a User object from a JSON save file.

        Args:
            file_path (str): The path to the JSON save file.
            api_key (str): The API key required for accessing Riot API.

        Returns:
            User: A User object created from the data in the JSON file.
        """

        with open(file_path, "r") as json_file:
            user_data = json.load(json_file)

        # Extract Riot ID data from the loaded JSON
        riot_id = {
            "summoners_name": user_data["summoners_name"],
            "summoners_tag": user_data["summoners_tag"],
            "encoded_summoners_name": user_data["encoded_summoners_name"],
            "encoded_summoners_tag": user_data["encoded_summoners_tag"],
        }

        # Create and return a new User object
        return cls(
            riot_id,
            api_key,
            puuid=user_data["puuid"],
            solo_duo_matchs_list=user_data["solo_duo_matchs_list"],
            flex_matchs_list=user_data["flex_matchs_list"],
        )

    def save(self):
        """
        Saves the User object as a JSON file.
        """
        self.create_data_folder_if_missing()
        user_path = self.create_user_folder_if_missing()
        saving_path = os.path.join(user_path, "identity.json")
        with open(saving_path, "w+") as json_file:
            json.dump(self.__dict__, json_file)

    def create_data_folder_if_missing(self):
        """
        Creates a 'data' folder if it does not already exist.

        This function checks if a folder named 'data' exists in the current directory.
        If the folder exists, it prints a message indicating this. If the folder does not exist,
        it creates the 'data' folder and prints a message indicating that it has been created.
        """
        data_folder_exists = check_if_folder_exists("data")
        if data_folder_exists:
            print("Data folder already exists.")
        else:
            os.mkdir("data")
            print("Data folder created.")

    def create_user_folder_if_missing(self):
        """
        Creates a user data folder if it does not already exist.

        This function constructs a folder name from the summoner's name and tag,
        checks if a folder with this name exists in the "./data" directory,
        and creates the folder if it is missing. If the folder already exists,
        it prints a message indicating this.
        """
        user_data_folder_name = f"{self.summoners_name}#{self.summoners_tag}"
        user_data_folder_path = os.path.join("data", user_data_folder_name)
        user_data_folder_exists = check_if_folder_exists(user_data_folder_path)
        if user_data_folder_exists:
            print(f"User {user_data_folder_name} folder already exists.")
        else:
            os.mkdir(user_data_folder_path)
            print(f"User {user_data_folder_name} folder has been created.")
        return user_data_folder_path

    def get_puuid(self, api_key: str) -> str:
        """
        Retrieves the PUUID (Player Universal Unique Identifier) from Riot Games API.

        Args:
            api_key (str): The API key for authenticating the request to the Riot Games API.

        Returns:
            str: The PUUID as a string.

        Raises:
            Exception: If the request to the Riot Games API fails (non-200 status code).
        """

        req = get(
            f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.summoners_name}/{self.summoners_tag}?api_key={api_key}"
        )

        if req.status_code == 200:
            response = req.json()
        else:
            raise Exception(f"Non-success status code: {req.status_code}")

        return response["puuid"]

    def list_matchs(
        self, matchs_list: list, start_index: int, api_key: str, queue: int
    ) -> list:
        """
        Recursively retrieves a list of match IDs from the Riot Games API.

        Args:
            matchs_list (list): A list to accumulate match IDs across recursive calls.
            start_index (int): The starting index for the API call.
            api_key (str): The API key for authenticating the request to the Riot Games API.
            queue (int): The queue type to filter the matches.
                        420 is for 5v5 Ranked Solo games.
                        440 is for 5v5 Ranked Flex games.

        Returns:
            list: A list containing all the match IDs from the paginated API.

        Raises:
            Exception: If the request to the Riot Games API fails (non-200 status code).
        """
        print(f"Sending api call with start index {start_index}")
        req = get(
            f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?queue={queue}&start={start_index}&count=100&api_key={api_key}"
        )

        if req.status_code == 200:
            matchs_list += req.json()

            if len(req.json()) == 100:
                return self.list_matchs(
                    matchs_list=matchs_list,
                    start_index=start_index + 100,
                    api_key=api_key,
                    queue=queue,
                )
            else:
                return matchs_list
        else:
            raise Exception(f"Non-success status code: {req.status_code}")
