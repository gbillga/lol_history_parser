from dotenv import load_dotenv
from utils import (
    get_api_key,
    create_account_info,
    get_list_summoners,
)
import os
from user import User
from collection import Collection
from db_management import DB

load_dotenv()

api_key = get_api_key()

list_summoners = get_list_summoners("account_list.json")

user_collection = Collection(api_key=api_key)

refresh_user = os.getenv("AUTO_REFRESH_USER")

for summoner in list_summoners:
    riot_id = create_account_info(summoner)
    folder_name = riot_id["summoners_name"] + "#" + riot_id["summoners_tag"]

    if folder_name not in user_collection.user_paths.keys():
        player = User(riot_id=riot_id, api_key=api_key)
        player.save()
    elif refresh_user == 1:
        print(
            f"User {folder_name} is already in the user collection, checking for new matches."
        )
        user_collection.user_objects[folder_name].refresh_user_matches(api_key)
        user_collection.user_objects[folder_name].save()

user_collection.refresh_collection(api_key=api_key)
user_collection.fetch_collection_matchs(api_key=api_key)
user_collection.create_aggregate_data()

db = DB()
written_rows = db.write_trd_df_to_rfd(
    dataset_name="aggregate_data.csv", table_name="games"
)

print(f"\n{written_rows} rows have been written.")
