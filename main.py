from dotenv import load_dotenv
from utils import get_api_key, create_account_info, get_list_summoners
from user import User
import os

load_dotenv()

api_key = get_api_key()

list_summoners = get_list_summoners("account_list.json")

for summoner in list_summoners:
    riot_id = create_account_info(summoner)
    folder_name = riot_id["summoners_name"] + "#" + riot_id["summoners_tag"]
    player_identity_path = os.path.join("data", folder_name, "identity.json")
    if not os.path.exists(player_identity_path):
        player = User(riot_id=riot_id, api_key=api_key)
        player.save()
    else:
        player = User.load_from_json(file_path=player_identity_path, api_key=api_key)

    player.create_data_folder_if_missing()
    player.create_user_folder_if_missing()
    player.create_matchs_folder_if_missing()

    match = "EUW1_6957197478"

    if match in player.find_unfetched_matchs():
        player.fetch_match(match_id=match, api_key=api_key)
