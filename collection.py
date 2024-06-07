import json
import os
import pandas as pd
import re
import time
from utils import check_if_folder_exists
from user import User


class Collection:
    def __init__(self, api_key: str) -> None:
        self.create_data_folder_if_missing()
        self.refresh_collection(api_key)

    def create_data_folder_if_missing(self):
        """
        Creates a 'data' folder if it does not already exist.

        This function checks if a folder named 'data' exists in the current directory.
        If the folder exists, it prints a message indicating this. If the folder does not exist,
        it creates the 'data' folder and prints a message indicating that it has been created.
        """
        data_layers = ["raw","trd","rfd"]
        if check_if_folder_exists("data"):
            print("Data folder already exists.")
        else:
            os.mkdir("data")
            print("Data folder created.")

        # Create each data layer
        for layer in data_layers:
            layer_path = os.path.join("data",layer)
            if check_if_folder_exists(layer_path):
                print(f"Data layer {layer} folder already exists.")
            else:
                os.mkdir(layer_path)
                print(f"Data layer {layer} folder created.")

    def refresh_collection(self, api_key: str) -> None:
        data_path = "data/raw"
        user_and_paths = {}
        user_object_dict = {}
        pattern = re.compile(r"^.{0,20}#.{2,6}$")

        for file in os.listdir(data_path):
            if os.path.isdir(os.path.join(data_path, file)) and re.match(
                pattern=pattern, string=file
            ):
                user_and_paths[file] = os.path.join(data_path, file)

        self.user_paths = user_and_paths

        for user in self.user_paths.keys():
            user_object_dict[user] = User.load_from_json(
                file_path=os.path.join(user_and_paths[user], "identity.json"),
                api_key=api_key,
            )

        self.user_objects = user_object_dict

    def fetch_collection_matchs(self, api_key: str) -> None:
        """
        Fetch unfetched matches for all users in the collection and update their match data.

        This method iterates through all user objects, identifies matches that haven't been fetched yet,
        and fetches match details using the provided API key. It keeps track of the number of requests made
        and pauses for a specified duration after every 100 requests to avoid hitting rate limits.

        Parameters:
        api_key (str): The API key used to authenticate the match fetch requests.

        Returns:
        None

        Raises:
        None

        Notes:
        - The function assumes that each user object has methods `find_unfetched_matchs` to get unfetched matches
        and `fetch_match` to fetch match details.
        - The function also assumes that user objects have attributes `solo_duo_matchs_list` and `flex_matchs_list`
        containing the match IDs.
        - To prevent exceeding API rate limits, the function pauses for 120 seconds after every 100 requests.
        """
        request_count = 0
        for user in self.user_objects.keys():
            print(f"Starting refreshing user : {user}")
            user_object = self.user_objects[user]
            user_object.create_user_folder_if_missing()
            user_object.create_matchs_folder_if_missing()
            unfetched_matchs = user_object.find_unfetched_matchs()
            for match in (
                user_object.matches_list
            ):
                if match in unfetched_matchs:
                    request_count += 1
                    if request_count % 100 == 0 and request_count != 0:
                        print("\n\n===== I'm sleepy let's have a small nap =====n\n")
                        time.sleep(120)

                    user_object.fetch_match(match_id=match, api_key=api_key)
            print("\n\n")

    def create_aggregate_data(self) -> None:
        """
        Aggregates match data for all users into a single CSV file.

        This method processes match data files for each user in `self.user_objects`, extracts relevant
        match and participant information, and combines the data into a pandas DataFrame. The resulting
        DataFrame is then saved as a CSV file named "aggregate_data.csv" in the "data" directory.

        The method performs the following steps:
        1. Iterates over all users in `self.user_objects`.
        2. Reads match files for each user from the corresponding directory.
        3. Extracts match information and participant data for the user.
        4. Combines the extracted data into a single DataFrame.
        5. Saves the DataFrame as a CSV file.

        Args:
            None

        Returns:
            None

        Raises:
            FileNotFoundError: If any match file is not found.
            KeyError: If expected keys ('info', 'participants', 'teams', etc.) are missing in the match files.

        Example:
            >>> obj = YourClassWithUserObjects()
            >>> obj.create_aggregate_data()
            # This will process the match data and create "data/aggregate_data.csv"
        """
        all_matches = []
        for user in self.user_objects.keys():
            user_object = self.user_objects[user]
            user_matchs_folder_path = os.path.join("data/raw", user, "matchs")
            for match in os.listdir(user_matchs_folder_path):
                match_file_path = user_matchs_folder_path + "/" + match
                with open(match_file_path, encoding="utf-8") as f:
                    match_info = json.load(f)["info"]
                    match_info["summoner_folder"] = user
                    participants = match_info["participants"]
                    participant_info = dict()
                    del match_info["participants"]
                    del match_info["teams"]
                    for participant in participants:
                        if participant["puuid"] == user_object.puuid:
                            participant_info = participant
                    if len(participant_info) > 0:
                        match_info.update(participant_info)
                        all_matches.append(match_info)
                    else:
                        print(
                            "Could not find corresponding participant information, disregarding game"
                        )
        all_matches = pd.DataFrame(all_matches)
        print(all_matches)

        all_matches.to_csv("data/trd/aggregate_data.csv", index=False)
