from dotenv import load_dotenv
from utils import get_api_key, get_riotid
from user import User

load_dotenv()

riot_id = get_riotid()
api_key = get_api_key()

neuneu = User(riot_id=riot_id,api_key=api_key)

neuneu.save()
