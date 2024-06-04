import os
import re
import time
from user import User


class Collection:
    def __init__(self, api_key: str) -> None:
        self.refresh_collection(api_key)

    def refresh_collection(self, api_key: str) -> None:
        data_path = "data"
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
            user_object.create_data_folder_if_missing()
            user_object.create_user_folder_if_missing()
            user_object.create_matchs_folder_if_missing()
            unfetched_matchs = user_object.find_unfetched_matchs()
            for match in (
                user_object.solo_duo_matchs_list + user_object.flex_matchs_list
            ):
                if match in unfetched_matchs:
                    request_count += 1
                    if request_count % 100 == 0 and request_count != 0:
                        print("\n\n===== I'm sleepy let's have a small nap =====n\n")
                        time.sleep(120)

                    user_object.fetch_match(match_id=match, api_key=api_key)
            print("\n\n")
