import time
from pyrogram import Client, filters
import logging
from pydeezer import Deezer
import deezer as deez
from deezloader.deezloader import DeeLogin 
from deezloader.spotloader import SpoLogin
from deezloader import easy_spoty
from deezloader.deezloader.dee_api import API
import traceback
from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Create a client connection to your MongoDB instance
mongo_url = 'mongodb+srv://nekozuX:farih2009@nekozu.wlvpzbo.mongodb.net/?retryWrites=true&w=majority&appName=nekozu'
client = MongoClient(mongo_url)
db = client['nekozu']  # replace with your database name
users_collection = db['users']# replace with your collection name

client_credentials_manager = SpotifyClientCredentials(client_id='70f6025a56d04d8ca55cf9a83596503d', client_secret='4fd4b6de55ae413eac5539a61865815a')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def check_user_id(user_id):
    # Convert user_id to string before checking
    return users_collection.find_one({'user_id': str(user_id)}) is not None

def add_user_id(user_id):
    # This will add a new document with the user_id field set to user_id
    # If a document with the same user_id already exists, it will be replaced
    users_collection.replace_one({'user_id': user_id}, {'user_id': user_id}, upsert=True)

ap = API()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

StartTime = time.time()

LOGGER = logging.getLogger(__name__)

arl = "cdec2ecd74ce883cc632c34ddf8f1226b110a997a045f8b5a327ff57aea226066007f9f1de06b4911fa4aa0be64cf1242da32a7797069a2a63ab8fa1506589b17b8a683394345cd734f301344a91ed8165a6c148e598c30ddc5f236271b142ca"
deezer = Deezer()
user_info = deezer.login_via_arl(arl)

dez = deez.Client(app_id='662971', app_secret='cd1f27edcb7f2115804df2fe6418a41b')
downloa = DeeLogin(
            arl='cdec2ecd74ce883cc632c34ddf8f1226b110a997a045f8b5a327ff57aea226066007f9f1de06b4911fa4aa0be64cf1242da32a7797069a2a63ab8fa1506589b17b8a683394345cd734f301344a91ed8165a6c148e598c30ddc5f236271b142ca',
            email='farihmuhammad75@gmail.com',
            password='Farih2009@',
)

spodown = SpoLogin(
    email='nekozu@gnuweeb.org',
    pwd='Farih2009@'
)

#track_search_results = deezer.search_tracks("Who Am I - alan walker")
#print(track_search_results[0]['id'])
api = API()
# Extract track ID from the link
download_status = {}
spoty = easy_spoty.Spo()
# Get the track
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
# Download directory
download_dir = r'./musik'

# Telegram setup

api_id = '2374504'
api_hash = '2ea965cd0674f1663ec291313edcd333'
bot_token = '7024217904:AAHSU6W8qerIOUhIohMcI_90VrVYz2WVpCo'

# Create the client and connect to Telegram
app = Client("nekommuu", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

async def send_error_message(app, error):
    error_message = f"An error occurred:\n\n{traceback.format_exc()[:4096]}..." if len(traceback.format_exc()) > 4096 else traceback.format_exc()
    await app.send_message(6627730366, f"Error: {error_message}")
    print(error_message)
    
allowed_user_id = '6627730366'  # replace with the allowed user ID

@app.on_message(filters.command("add"))
async def add_user(client, message):
    if str(message.from_user.id) != allowed_user_id:
        return

    # Split the message text to get the user ID
    command, _, user_id = message.text.partition(' ')
    if not user_id:
        await message.reply_text("Please provide a user ID.")
        return

    if not check_user_id(user_id):
        add_user_id(user_id)
        await message.reply_text("User added!")
    else:
        await message.reply_text("User already exists!")

@app.on_message(filters.command("check"))
async def checkommand(client, message):
    if str(message.from_user.id) != allowed_user_id:
        return

    # Split the message text to get the user ID
    command, _, user_id = message.text.partition(' ')
    if not user_id:
        await message.reply_text("Please provide a user ID.")
        return

    if check_user_id(user_id):
        await message.reply_text("User exists!")
    else:
        await message.reply_text("User does not exist!")
        
@app.on_message(filters.command("remove"))
async def remove_user(client, message):
    if str(message.from_user.id) != allowed_user_id:
        return

    # Split the message text to get the user ID
    command, _, user_id = message.text.partition(' ')
    if not user_id:
        await message.reply_text("Please provide a user ID.")
        return

    if check_user_id(user_id):
        users_collection.delete_one({'user_id': user_id})
        await message.reply_text("User removed!")
    else:
        await message.reply_text("User does not exist!")
        
        


