from dotenv import load_dotenv
from utils import get_api_key, create_account_info, get_list_summoners
from user import User
from collection import Collection
import os

load_dotenv()

api_key = get_api_key()

list_summoners = get_list_summoners("account_list.json")

user_collection = Collection(api_key=api_key)

for summoner in list_summoners:
    riot_id = create_account_info(summoner)
    folder_name = riot_id["summoners_name"] + "#" + riot_id["summoners_tag"]

    if folder_name not in user_collection.user_paths.keys():
        player = User(riot_id=riot_id, api_key=api_key)
        player.save()
    else:
        print(f"User {folder_name} is already in the user collection.")

user_collection.refresh_collection(api_key=api_key)
user_collection.fetch_collection_matchs(api_key=api_key)