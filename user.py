import os
from utils import check_if_folder_exists
from requests import get
import json
import re


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
        self.summoners_region = riot_id["summoners_region"]
        self.encoded_summoners_name = riot_id["encoded_summoners_name"]
        self.encoded_summoners_tag = riot_id["encoded_summoners_tag"]
        self.puuid = (
            self.get_puuid(api_key=api_key)
            if "puuid" not in kwargs
            else kwargs["puuid"]
        )
        self.matches_list = (
            self.get_all_matches(api_key=api_key)
            if "matches_list" not in kwargs
            else kwargs["matches_list"]
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
            "summoners_region": user_data["summoners_region"],
            "encoded_summoners_name": user_data["encoded_summoners_name"],
            "encoded_summoners_tag": user_data["encoded_summoners_tag"],
        }
        # Create and return a new User object
        return cls(
            riot_id,
            api_key,
            puuid=user_data["puuid"],
            matches_list=user_data["matches_list"],
        )

    def save(self):
        """
        Saves the User object as a JSON file.
        """
        user_path = self.create_user_folder_if_missing()
        saving_path = os.path.join(user_path, "identity.json")
        with open(saving_path, "w+") as json_file:
            json.dump(self.__dict__, json_file)

    def create_user_folder_if_missing(self):
        """
        Creates a user data folder if it does not already exist.

        This function constructs a folder name from the summoner's name and tag,
        checks if a folder with this name exists in the "./data" directory,
        and creates the folder if it is missing. If the folder already exists,
        it prints a message indicating this.
        """
        user_data_folder_name = f"{self.summoners_name}#{self.summoners_tag}"
        user_data_folder_path = os.path.join("data/raw", user_data_folder_name)
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
            f"https://{self.summoners_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.summoners_name}/{self.summoners_tag}?api_key={api_key}"
        )

        if req.status_code == 200:
            response = req.json()
        else:
            raise Exception(f"Non-success status code: {req.status_code}")

        return response["puuid"]

    def refresh_user_matches(self, api_key: str) -> None:
        og_matches_number = len(self.matches_list)
        newly_feched_matches =  self.get_all_matches(api_key=api_key)
        self.matches_list = list(set(self.matches_list + newly_feched_matches))
        print(f"New matches found: {len(self.matches_list) - og_matches_number}")


    def get_all_matches(self, api_key: str) -> list:
        matches_list = []
        for queue in [400, 420, 430, 440, 450]:
            matches_list.extend(self.get_matches_by_queue(matchs_list=[], start_index=0, api_key=api_key, queue=queue))
        return matches_list

    def get_matches_by_queue(
        self, matchs_list: list, start_index: int, api_key: str, queue: int
    ) -> list:
        """
        Recursively retrieves a list of match IDs from the Riot Games API.

        Args:
            matchs_list (list): A list to accumulate match IDs across recursive calls.
            start_index (int): The starting index for the API call.
            api_key (str): The API key for authenticating the request to the Riot Games API.
            queue (int): The queue type to filter the matches.
                        400 is for 5v5 Normal Draft.
                        420 is for 5v5 Ranked Solo games.
                        430 is for 5v5 Normal Blind.
                        440 is for 5v5 Ranked Flex games.
                        450 is for ARAM.
        Returns:
            list: A list containing all the match IDs from the paginated API.

        Raises:
            Exception: If the request to the Riot Games API fails (non-200 status code).
        """
        print(f"Sending api call with start index {start_index}")
        req = get(
            f"https://{self.summoners_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{self.puuid}/ids?queue={queue}&start={start_index}&count=100&api_key={api_key}"
        )

        if req.status_code == 200:
            matchs_list += req.json()

            if len(req.json()) == 100:
                return self.get_matches_by_queue(
                    matchs_list=matchs_list,
                    start_index=start_index + 100,
                    api_key=api_key,
                    queue=queue,
                )
            else:
                return matchs_list
        else:
            raise Exception(f"Non-success status code: {req.status_code}")

    def create_matchs_folder_if_missing(self):
        """
        Creates a folder for storing match files if it does not already exist.

        This function constructs a folder path based on the summoner's name and tag,
        and checks if the folder exists. If the folder does not exist, it creates
        the folder and prints a confirmation message. If the folder already exists,
        it prints a message indicating so.

        Attributes:
            self.summoners_name (str): The summoner's name.
            self.summoners_tag (str): The summoner's tag.

        Side effects:
            Creates a directory at the specified path if it doesn't exist.
            Prints a message indicating whether the directory was created or already existed.
        """
        user_data_folder_name = f"{self.summoners_name}#{self.summoners_tag}"
        user_matchs_folder_path = os.path.join("data/raw", user_data_folder_name, "matchs")
        user_data_folder_exists = check_if_folder_exists(user_matchs_folder_path)
        if user_data_folder_exists:
            print(f"User {user_data_folder_name} matchs folder already exists.")
        else:
            os.mkdir(user_matchs_folder_path)
            print(f"User {user_data_folder_name} matchs folder has been created.")

    def find_unfetched_matchs(self) -> list:
        """
        Finds matches that have not yet been fetched.

        This function checks the match files already present in the user's match folder
        and compares them against a list of match files that should be fetched. It
        returns a list of match files that are not yet fetched.

        Attributes:
            self.summoners_name (str): The summoner's name.
            self.summoners_tag (str): The summoner's tag.
            self.flex_matchs_list (list): List of flex match files to be fetched.
            self.solo_duo_matchs_list (list): List of solo/duo match files to be fetched.

        Returns:
            list: A list of match files that have not yet been fetched.

        Side effects:
            None.
        """
        user_data_folder_name = f"{self.summoners_name}#{self.summoners_tag}"
        user_matchs_folder_path = os.path.join("data/raw", user_data_folder_name, "matchs")
        matchs_folder_content = os.listdir(user_matchs_folder_path)
        already_fetched_files = []
        matchs_to_be_fetched = []
        pattern = re.compile(r"^[a-zA-Z0-9]{2,5}_[0-9]+\.json$")

        # List already fetched matchs
        for file in matchs_folder_content:
            if re.match(pattern=pattern, string=file):
                already_fetched_files.append(file.split(".json")[0])

        # Check if identity matchs are fetched, if not add to output list
        for match in self.flex_matchs_list + self.solo_duo_matchs_list:
            if match not in already_fetched_files:
                matchs_to_be_fetched.append(match)

        return matchs_to_be_fetched

    def fetch_match(self, match_id: str, api_key: str):
        """
        Fetches a match from the Riot Games API and saves it to the user's match folder.

        This function sends a request to the Riot Games API to fetch the match data
        corresponding to the given match ID and saves the response as a JSON file
        in the user's match folder. The size of the saved file is printed upon
        successful fetch. If the request fails, an exception is raised.

        Parameters:
            match_id (str): The ID of the match to fetch.
            api_key (str): The API key for authenticating the request.

        Attributes:
            self.summoners_name (str): The summoner's name.
            self.summoners_tag (str): The summoner's tag.

        Raises:
            Exception: If the API request returns a non-success status code.

        Side effects:
            Sends a GET request to the Riot Games API.
            Writes the fetched match data to a JSON file in the user's match folder.
            Prints the size of the fetched match file.
        """
        user_data_folder_name = f"{self.summoners_name}#{self.summoners_tag}"
        user_matchs_folder_path = os.path.join("data/raw", user_data_folder_name, "matchs")
        print(f"Match {match_id} will be fecthed")
        req = get(
            f"https://{self.summoners_region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
        )

        if req.status_code == 200:
            saving_path = os.path.join(user_matchs_folder_path, f"{match_id}.json")
            with open(saving_path, "w+") as json_file:
                json.dump(req.json(), json_file)

            file_size = round(os.stat(saving_path).st_size / (1024 * 1024), 2)
            print(
                f"Match {match_id} from user {user_data_folder_name} has been fetched, size : {file_size} Mo."
            )
        elif req.status_code == 404:
            print(
                f"Match {match_id} from user {user_data_folder_name} can not be found."
            )
        else:
            raise Exception(f"Non-success status code: {req.status_code}")