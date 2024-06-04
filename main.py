from dotenv import load_dotenv
from utils import get_api_key, get_riotid
from user import User
import os

load_dotenv()

riot_id = get_riotid()
api_key = get_api_key()

folder_name = riot_id["summoners_name"] + "#" + riot_id["summoners_tag"]
neuneu_identity_path = os.path.join("data", folder_name, "identity.json")

neuneu = User.load_from_json(file_path=neuneu_identity_path, api_key=api_key)

neuneu.create_data_folder_if_missing()
neuneu.create_user_folder_if_missing()
neuneu.create_matchs_folder_if_missing()

match = "EUW1_6957197478"

if match in neuneu.find_unfetched_matchs():
    neuneu.fetch_match(match_id=match, api_key=api_key)
