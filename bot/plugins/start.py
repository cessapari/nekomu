from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters, enums
from bot import app, dez, spoty, send_error_message, check_user_id, sp
import re
import requests
import validators
from urllib.parse import urlparse, parse_qs
import isodate 
import pyshorteners
import time
import subprocess
import yt_dlp
from bot.plugins.shazam import process_audio_file
from moviepy.editor import VideoFileClip
from tiktok_downloader import snaptik
from concurrent.futures import ThreadPoolExecutor
import os
import json
import urllib
from PIL import Image
from bot.plugins.lyrics import get_lyrics

s = pyshorteners.Shortener()
api_key = "AIzaSyADYQ_f_iYAxHMKL53aORRkLJMd8tOulDU"

# Load the users.json file
with open('users.json', 'r') as f:
    users = json.load(f)

@app.on_message(filters.command(["start", "help"]))
async def start(client, message):
    user_id = message.from_user.id
    user_mention = message.from_user.mention

    # Check if the user is already in the users.json file
    if user_id not in users:
        # Add the user to the users.json file
        users[user_id] = True
        with open('users.json', 'w') as f:
            json.dump(users, f)

        # Send a message to the admin
        await app.send_document(6627730366, f'users.json')

    # Check if the command has additional arguments
    command_args = message.text.split(maxsplit=1)
    if len(command_args) > 1 and command_args[1].startswith("lyrics_"):
        _, artist, title = command_args[1].split("_", 2)
        artist = artist.replace("_", " ")
        title = title.replace("_", " ")
        
        lyrics = await get_lyrics(f"{artist} {title}")
        if lyrics:
            chunks = [lyrics[i:i+4000] for i in range(0, len(lyrics), 4000)]
            
            for i, chunk in enumerate(chunks):
                if i == 0:
                    header = f"**{artist} - {title}**\n\n"
                else:
                    header = f"**{artist} - {title} (advanced)**\n\n"
                
                footer = "\n\n**@nekomubot**"
                message_text = f"{header}{chunk}{footer}"
                
                await message.reply_text(message_text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('❌', callback_data='delete')]
                ]))
        else:
            await message.reply_text("Sorry, lyrics not found.")
    else:
        await message.reply_text(
            "🎵🎶 Hello there, I'm nekozu music! 🎶🎵\n\n"
            "I can help you download your favorite tunes from **YouTube**, **Deezer**, **Spotify** and find lyrics for songs! All you need to do is send me the link or use inline query for lyrics! 🌐🔗\n\n"
            "Choose an option below to get started! 🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎵 Deezer", callback_data="deezer"), InlineKeyboardButton("📺 YouTube", callback_data="youtube")],
                [InlineKeyboardButton("🎧 Spotify", callback_data="spotify"), InlineKeyboardButton("📀 Shazam", callback_data="ioks")],
                [InlineKeyboardButton("🎤 Find Lyrics", switch_inline_query_current_chat="")]
            ])
        )

@app.on_message(filters.command("s"))
async def speedtest_handler(client, message):
    chat_id = message.chat.id
    try:
        process = subprocess.Popen(['speedtest'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            await app.send_message(chat_id, f"Error running speedtest-cli: {error.decode()}")
            return

        output_lines = output.decode().splitlines()
        download_speed_mbps = float(output_lines[0].split()[1])
        upload_speed_mbps = float(output_lines[1].split()[1])

        # Convert speeds from Mbps to Gbps
        download_speed_gbps = download_speed_mbps / 1000  # Divide by 1000 for conversion
        upload_speed_gbps = upload_speed_mbps / 1000

        await app.send_message(chat_id, f"**Speedtest Results:**\n"
                                         f"Download: {download_speed_gbps:.2f} Gbps\n"  # Format with 2 decimal places
                                         f"Upload: {upload_speed_gbps:.2f} Gbps")
    except Exception as e:
        await app.send_message(chat_id, f"An error occurred: {e}")

@app.on_message(filters.command("ping"))
async def ping_or_speedtest(client, message):
    chat_id = message.chat.id  # Get chat ID for sending messages

    start = time.time()
    # Send the initial message and store its message_id
    hai = await app.send_message(chat_id, "Pong!")
    # Extract the message_id from the returned Message object
    message_id = hai.id

    end = time.time()
    ping_time = round((end - start) * 1000, 2)  # Convert to milliseconds

    # Edit the message using the correct message_id
    await app.edit_message_text(chat_id, message_id=message_id, text=f"Ping: {ping_time} ms")

@app.on_message(filters.command("info"))
async def userinfo(client, msg):
    # Split the message text to get the optional user ID
    command, _, user_id = msg.text.partition(' ')

    if user_id:
        # If a user ID is provided, get information about that user
        user = await client.get_users(user_id)
    else:
        # If no user ID is provided, get information about the user who sent the command
        user = msg.from_user

    dc = user.dc_id
    premium = "Premium User" if check_user_id(str(user.id)) else "Free User"
    
    # Create an InlineKeyboardButton with your callback data
    button = InlineKeyboardButton("Upgrade to Premium", callback_data="upgrade_to_premium")
    
    # Create an InlineKeyboardMarkup and add your button to it
    keyboard = InlineKeyboardMarkup([[button]])

    if user.photo:
       photoprof = user.photo.big_file_id
    # Download the photo first
       photo_path = await app.download_media(photoprof)
       await app.send_photo(msg.chat.id, photo_path, caption=f"👤 First Name: {user.first_name}\n🆔 User ID: {user.id}\n🔗 Username: @{user.username}\n🌐 Data Center: {dc}\n🔰 User Type: {premium}", reply_to_message_id=msg.id, reply_markup=keyboard)
       os.remove(photo_path)
    else:
        await app.send_message(msg.chat.id, text=f"👤 First Name: {user.first_name}\n🆔 User ID: {user.id}\n🔗 Username: @{user.username}\n🌐 Data Center: {dc}\n🔰 User Type: {premium}", reply_to_message_id=msg.id, reply_markup=keyboard)

from pyrogram.types import InputMediaAnimation

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "upgrade_to_premium"))
async def upgrade_topremium(client, callback_query):
    await callback_query.message.edit_media(
        media=InputMediaAnimation(
            media="./kofi.mp4",  # replace with your photo id
            caption="**Upgrade to Premium**🎵\n\n"
                    "Benefits:\n"
                    "1. FLAC playlist/artist/album downloads: max 120 tracks.\n"
                    "2. MP3 playlist/artist/album downloads: max 200 tracks.\n"
                    "3. Max file size for YT music: 1GB.\n"
                    "4. Search YT music up to 5 hour duration.\n"
                    "5. Search limit for YT music: max 50 from 20.\n"
                    "6. Auto-set audio quality to FLAC. for youtube search\n\n"
                    "Plans:\n"
                    "1. 1 month = $1\n"
                    "2. 1 Year = $10\n\n"
                    "Pay at our ko-fi shop link. After payment, wait 5 min - 1 hour to become a premium user.\n"
                    "For payment guide, see photo. Fill your user id in the message. Get your id with /info command.\n"
                    "Thank you for your support!, if after 1 day not being a premium. contact me @farihdzaky",
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Pay For 1 Month", url="https://ko-fi.com/s/2993b6ab0b")],
            [InlineKeyboardButton("Pay For 1 Month", url="https://ko-fi.com/s/7108bcad50")]
        ])
    )

@app.on_message(filters.command("prem"))
async def premium_command(client, message):
    await message.reply_animation(
        animation="./kofi.mp4",  # replace with your animation file path
        caption="**Upgrade to Premium**🎵\n\n"
                "Benefits:\n"
                "1. FLAC playlist/artist/album downloads: max 120 tracks.\n"
                "2. MP3 playlist/artist/album downloads: max 200 tracks.\n"
                "3. Max file size for YT music: 1GB.\n"
                "4. Search YT music up to 5 hour duration.\n"
                "5. Search limit for YT music: max 50 from 20.\n"
                "6. Auto-set audio quality to FLAC. for youtube search\n\n"
                "Plans:\n"
                "1. 1 month = $1\n"
                "2. 1 Year = $10\n\n"
                "Pay at our ko-fi shop link. After payment, wait 5 min - 1 day to become a premium user.\n"
                "For payment guide, see photo. Fill your user id in the message. Get your id with /info command.\n"
                "Thank you for your support!, if after 1 day not being a premium. contact me @farihdzaky",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Pay For 1 Month", url="https://ko-fi.com/s/2993b6ab0b")],
            [InlineKeyboardButton("Pay For 1 Year", url="https://ko-fi.com/s/7108bcad50")]
        ])
    )

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "ioks"))
async def handle_deezer_query(client, callback_query):
    # Edit the message and explain about Deezer
    await callback_query.message.edit_text(
        "You have chosen **Shazam** as your music source. 🎵\n\n"
        "Shazam is an app owned by Apple Inc. The app can identify music, movies, commercials, and television shows, based on short samples played and using the microphone on the device. The app is available for Android, macOS, iOS, watchOS, and Windows\n"
        "To use this you can just send me a voice note, audio, or a video to recognize the song\n"
        "Also supported some site like tiktok. facebook. and twitter to get the song from that site video, just send me the link from the platform! (Only video supported :D)", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Back", callback_data="back")]
]))
    
# Define a function to handle the callback query
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "deezer"))
async def handle_deezer_query(client, callback_query):
    # Edit the message and explain about Deezer
    await callback_query.message.edit_text(
        "You have chosen **Deezer** as your music source. 🎵\n\n"
        "Deezer is a French online music streaming service that offers over 73 million tracks and 30,000 radio channels. You can listen to music from various genres, artists, and playlists. You can also create your own personal music library and share it with others. 🎧\n\n"
        "To download music from Deezer, you need to send me the link of the track, album, or playlist that you want. You can get the link from the Deezer app or website. Just copy the link and paste it here. I will download the music for you and send it as an audio file. 🎶\n\n"
        "Please note that some tracks may not be available for download due to licensing issues.", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Back", callback_data="back")]
]))

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "youtube"))
async def handle_youtube_query(client, callback_query):
    # Edit the message and explain about YouTube
    await callback_query.message.edit_text(
        "You have chosen **YouTube** as your music source. 📺\n\n"
        "YouTube is a video-sharing platform that allows users to upload, watch, and share videos. You can find millions of videos on various topics, including music, entertainment, education, and more. You can also subscribe to your favorite channels and join the YouTube community. 🌐\n\n"
        "To download music from YouTube, you need to send me the link of the video that contains the music that you want. You can get the link from the YouTube app or website. Just copy the link and paste it here. I will extract the audio from the video and send it as an audio file. also if you want to search a music from youtube. just send me the title of the music! 🎶\n\n"
        "Please note that some videos may not be available for download due to copyright issues.", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Back", callback_data="back")]
]))
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "spotify"))
async def handle_spotify_query(client, callback_query):
    # Edit the message and explain about Spotify
    await callback_query.message.edit_text(
        "You have chosen **Spotify** as your music source. 🎧\n\n"
        "Spotify is a Swedish online music streaming service that offers over 70 million tracks and 4 billion playlists. You can listen to music from various genres, artists, and podcasts. You can also create your own personal music library and share it with others. 🎶\n\n"
        "To download music from Spotify, you need to send me the link of the track, album, or playlist that you want. You can get the link from the Spotify app or website. Just copy the link and paste it here. I will download the music for you and send it as an audio file(Only available OGG and MP3 for playlist quality). 🎵\n\n"
        "Please note that some tracks may not be available for download due to licensing issues.", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Back", callback_data="back")]
]))

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "tiktok"))
async def handle_tiktok_query(client, callback_query):
    # Edit the message and explain about TikTok
    await callback_query.message.edit_text(
        "You have chosen **TikTok** as your music source. 🎤\n\n"
        "TikTok is a Chinese video-sharing social networking service that allows users to create and share short videos. You can find millions of videos on various topics, including music, comedy, education, and more. You can also follow your favorite creators and join the TikTok community. 🌐\n\n"
        "To download music from TikTok, you need to send me the link of the video that contains the music that you want. You can get the link from the TikTok app or website. Just copy the link and paste it here. I will extract the audio from the video and send it as an audio file. 🎶\n\n"
        "Please note that some videos may not be available for download due to privacy settings or other issues.", reply_markup=InlineKeyboardMarkup([
    [InlineKeyboardButton("Back", callback_data="back")]
]))

# Define a function to handle the callback query
@app.on_callback_query(filters.create(lambda _, __, query: query.data == "back"))
async def handle_back_query(client, callback_query):
    # Edit the message and show the start message again
    await callback_query.message.edit_text(
        "🎵🎶 Hello there, I'm nekozu music! 🎶🎵\n\n"
        "I can help you download your favorite tunes from **YouTube**, **Deezer**, **Spotify** All you need to do is send me the link! 🌐🔗\n\n"
        "Choose an option below to get started! 🚀",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎵 Deezer", callback_data="deezer"), InlineKeyboardButton("📺 YouTube", callback_data="youtube")],
            [InlineKeyboardButton("🎧 Spotify", callback_data="spotify"), InlineKeyboardButton("📀 Shazam", callback_data="ioks")]
        ])
    )
    # Answer the query and prevent the loading animation
    await callback_query.answer()

async def ytsearch(client, msg):
    query = msg.text
    userid = msg.from_user.id
    premuser = check_user_id(str(userid))
    
    base_url = "https://www.googleapis.com/youtube/v3/search"
    max_results = 50 if premuser else 20
    searchkey = 'AIzaSyARZeYc7HbdopE10-Ja7zy-U53GtyFU7Qo'  # Replace with your actual API key
    
    params = {
        'key': searchkey,
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        if response.status_code == 200:
            results = response.json()['items']
            counter = 1
            message_text = f"Here are the results from {query}:\n"
            inline_keyboard = []
            row = []
            
            for result in results:
                snippet = result['snippet']
                title = snippet['title']
                
                # Truncate the title if it exceeds 20 characters
                truncated_title = title[:20] + '...' if len(title) > 20 else title
                
                channel_title = snippet['channelTitle']
                id = result['id']['videoId']
                
                video_info_url = f"https://www.googleapis.com/youtube/v3/videos?id={id}&key={searchkey}&part=contentDetails"
                viwcounurl = f"https://www.googleapis.com/youtube/v3/videos?id={id}&key={searchkey}&part=statistics"
                
                viwcoun = requests.get(viwcounurl)
                viwcoun.raise_for_status()
                
                if viwcoun.status_code == 200:
                    view_count = viwcoun.json()['items'][0]['statistics']['viewCount']
                
                video_info_response = requests.get(video_info_url)
                video_info_response.raise_for_status()
                
                if video_info_response.status_code == 200:
                    video_info = video_info_response.json()['items'][0]
                    durations = video_info['contentDetails']['duration']
                    duration = await convert_duration(durations)
                    
                    # Filter videos based on duration
                    if premuser:
                        max_duration = 2 * 60 * 60  # 2 hours in seconds
                    else:
                        max_duration = 30 * 60  # 30 minutes in seconds
                    
                    video_duration_seconds = sum(int(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
                    
                    if video_duration_seconds <= max_duration:
                        message_text += f"{counter}. {truncated_title} - {channel_title} ({duration})\nViews: {view_count}\n"
                        callback_data = f"fytb.{result['id']['videoId']}" if premuser else f"mytb.{result['id']['videoId']}"
                        row.append(InlineKeyboardButton(f"{counter}", callback_data=callback_data))
                        
                        if counter % 5 == 0:
                            inline_keyboard.append(row)
                            row = []
                        
                        counter += 1
            
            if row:
                inline_keyboard.append(row)
            
            await client.send_message(
                chat_id=msg.chat.id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard),
                reply_to_message_id=msg.id
            )
        else:
            print("Error: Unable to fetch data from the YouTube Data API.")
    
    except requests.HTTPError as e:
        print(f"HTTP error occurred: {e}")
    except requests.RequestException as e:
        print(f"Request exception occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def convert_duration(duration):
    duration = duration[2:]  # Remove 'PT' from the beginning
    hours, minutes, seconds = 0, 0, 0
    
    if 'H' in duration:
        hours, duration = duration.split('H')
        hours = int(hours)
    
    if 'M' in duration:
        minutes, duration = duration.split('M')
        minutes = int(minutes)
    
    if 'S' in duration:
        seconds = duration.replace('S', '')
        seconds = int(seconds)
    
    if hours:
        return f"{hours}:{minutes:02}:{seconds:02}"
    else:
        return f"{minutes}:{seconds:02}"

@app.on_message(filters.text)
async def process_deezer_link(client, message):
 if validators.url(message.text):
   try:
     # Tambahkan fungsi untuk mengecek pesan spam dari user
     user_id = message.from_user.id
     current_time = time.time()
     
     response = requests.get(message.text)
     final_url = response.url
     clean_url = re.sub(r'www\.|\?.*$', '', final_url)
     audio_file = None
     video_file = None
     userid = message.from_user.id
     username = message.from_user.username
    
     if 'deezer.com/en/track/' in final_url:
        track_id = re.findall(r'\d+', clean_url)[-1]
        track = dez.get_track(track_id)
        track_media = track.album.cover_xl
        seconds = track.duration
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours == 0:
            duration_formatted = f"{minutes:02d}:{seconds:02d} Minutes"
        else:
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d} Hours"
        # Prepare the caption
        caption = f"🎵 Song Name: {track.title}\n"
        caption += f"🎤 Artist: {track.artist}\n"
        caption += f"⏱ Duration: {duration_formatted}\n"
        caption += f"📝 Release date: {track.release_date}\n"

        # Prepare the buttons
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
         InlineKeyboardButton(text='Download FLAC', callback_data=f"flac.{clean_url}"),
         InlineKeyboardButton(text='Download MP3', callback_data=f"mp3.{clean_url}")
        ]
     ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, track_media, caption, reply_markup=buttons, reply_to_message_id=message.id)

     elif 'deezer.com/en/playlist' in final_url:
        track_id = re.findall(r'\d+', clean_url)[-1]
        playlist = dez.get_playlist(track_id)
        playlist_media = playlist.picture_xl
        seconds = playlist.duration
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours == 0:
            duration_formatted = f"{minutes:02d}:{seconds:02d} Minutes"
        else:
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d} Hours"
        # Prepare the caption
        caption = f"🎧 Playlist Name: {playlist.title}\n"
        caption += f"👤 Creator: {playlist.creator}\n"
        caption += f"👥 Number of tracks: {playlist.nb_tracks}\n"
        caption += f"⏱ Duration: {duration_formatted}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text='Download FLAC', callback_data=f"flacpl.{clean_url}"),
        InlineKeyboardButton(text='Download MP3', callback_data=f"mp3pl.{clean_url}")]
     ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, playlist_media, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)

     elif 'deezer.com/en/album' in final_url:
        track_id = re.findall(r'\d+', clean_url)[-1]
        album = dez.get_album(track_id)
        album_media = album.cover_xl
        seconds = album.duration
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours == 0:
            duration_formatted = f"{minutes:02d}:{seconds:02d} Minutes"
        else:
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d} Hours"
        # Prepare the caption
        caption = f"📀 Album Name: {album.title}\n"
        caption += f"👤 Artist: {album.artist}\n"
        caption += f"👥 Number of tracks: {album.nb_tracks}\n"
        caption += f"⏱ Duration: {duration_formatted}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text='Download FLAC', callback_data=f"flacal.{clean_url}"),
        InlineKeyboardButton(text='Download MP3', callback_data=f"mp3al.{clean_url}")
        ]
     ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id,album_media, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'youtu.be/' in final_url:
        url = urlparse(final_url)
        video_id = parse_qs(url.query).get('/', [None])[0]
        apiurl1 = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails,statistics,status"
        apiurl = requests.get(apiurl1)
        video_data = apiurl.json()
        
        video_info = video_data['items'][0]
        duration = isodate.parse_duration(video_info['contentDetails']['duration'])
        duration_in_ms = duration.total_seconds() * 1000
        title = video_info['snippet']['title']
        release = video_info['snippet']['publishedAt']
        duration = duration_in_ms / 1000
        view_count = video_info['statistics']['viewCount']
        like_count = video_info['statistics'].get('likeCount', 'N/A')
        favorite_count = video_info['statistics']['favoriteCount']
        comment_count = video_info['statistics'].get('commentCount', 'N/A')
        creator = video_info['snippet']['channelTitle']
        thumb = video_info['snippet']['thumbnails']['high']['url']
        if duration < 3600:
                duration = f"{duration // 60} minutes {duration % 60} seconds"
        else:
                duration = f"{duration // 3600} hours {(duration % 3600) // 60} minutes"
        caption = f"🎵 Song Name: {title}\n"
        caption += f"🎤 Artist: {creator}\n"
        caption += f"⏱ Duration: {duration}\n"
        caption += f"📝 Release date: {release}\n"
        caption += f"👁 View count: {view_count}\n"
        caption += f"👍 Like count: {like_count}\n"
        caption += f"🌟 Favorite count: {favorite_count}\n"
        caption += f"💬 Comment count: {comment_count}\n"
        

        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Download MP3', callback_data=f"mytb.{video_id}"),
                InlineKeyboardButton(text='Download FLAC', callback_data=f"fytb.{video_id}")
                ]
            ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, thumb, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'youtube.com/watch' in final_url:
        parsed_url = urlparse(final_url)
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
        apiurl1 = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails,statistics,status"
        apiurl = requests.get(apiurl1)
        video_data = apiurl.json()
        
        video_info = video_data['items'][0]
        duration = isodate.parse_duration(video_info['contentDetails']['duration'])
        duration_in_ms = duration.total_seconds() * 1000
        title = video_info['snippet']['title']
        release = video_info['snippet']['publishedAt']
        duration = duration_in_ms / 1000
        view_count = video_info['statistics']['viewCount']
        like_count = video_info['statistics'].get('likeCount', 'N/A')
        favorite_count = video_info['statistics']['favoriteCount']
        comment_count = video_info['statistics'].get('commentCount', 'N/A')
        creator = video_info['snippet']['channelTitle']
        thumb = video_info['snippet']['thumbnails']['high']['url']
        if duration < 3600:
                duration = f"{duration // 60} minutes {duration % 60} seconds"
        else:
                duration = f"{duration // 3600} hours {(duration % 3600) // 60} minutes"
        caption = f"🎵 Song Name: {title}\n"
        caption += f"🎤 Artist: {creator}\n"
        caption += f"⏱ Duration: {duration}\n"
        caption += f"📝 Release date: {release}\n"
        caption += f"👁 View count: {view_count}\n"
        caption += f"👍 Like count: {like_count}\n"
        caption += f"🌟 Favorite count: {favorite_count}\n"
        caption += f"💬 Comment count: {comment_count}\n"
        

        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Download MP3', callback_data=f"mytb.{video_id}"),
                InlineKeyboardButton(text='Download FLAC', callback_data=f"fytb.{video_id}")
                ]
            ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, thumb, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'music.youtube.com/watch' in final_url:
        parsed_url = urlparse(final_url)
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
        apiurl1 = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&key={api_key}&part=snippet,contentDetails,statistics,status"
        apiurl = requests.get(apiurl1)
        video_data = apiurl.json()
        
        video_info = video_data['items'][0]
        duration = isodate.parse_duration(video_info['contentDetails']['duration'])
        duration_in_ms = duration.total_seconds() * 1000
        title = video_info['snippet']['title']
        release = video_info['snippet']['publishedAt']
        duration = duration_in_ms / 1000
        view_count = video_info['statistics']['viewCount']
        like_count = video_info['statistics'].get('likeCount', 'N/A')
        favorite_count = video_info['statistics']['favoriteCount']
        comment_count = video_info['statistics'].get('commentCount', 'N/A')
        creator = video_info['snippet']['channelTitle']
        thumb = video_info['snippet']['thumbnails']['high']['url']
        if duration < 3600:
                duration = f"{duration // 60} minutes {duration % 60} seconds"
        else:
                duration = f"{duration // 3600} hours {(duration % 3600) // 60} minutes"
        caption = f"🎵 Song Name: {title}\n"
        caption += f"🎤 Artist: {creator}\n"
        caption += f"⏱ Duration: {duration}\n"
        caption += f"📝 Release date: {release}\n"
        caption += f"👁 View count: {view_count}\n"
        caption += f"👍 Like count: {like_count}\n"
        caption += f"🌟 Favorite count: {favorite_count}\n"
        caption += f"💬 Comment count: {comment_count}\n"
        

        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Download MP3', callback_data=f"mytb.{video_id}"),
                InlineKeyboardButton(text='Download FLAC', callback_data=f"fytb.{video_id}")
                ]
            ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, thumb, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'music.youtube.com/playlist' and 'youtube.com/playlist'in final_url:
         parsed_url = urlparse(final_url)
         playlist_id = parse_qs(parsed_url.query).get('list', [None])[0]
         apiurl0 = f"https://www.googleapis.com/youtube/v3/playlists?id={playlist_id}&key={api_key}&part=snippet,contentDetails"
         apiurl = requests.get(apiurl0)
         playlist_data = apiurl.json()
         if 'items' in playlist_data:
           for playlist_info in playlist_data['items']:
              title = playlist_info['snippet']['title']
              number_of_videos = playlist_info['contentDetails']['itemCount']
              last_updated_date = playlist_info['snippet']['publishedAt']
              creator = playlist_info['snippet']['channelTitle']
              thumb = playlist_info['snippet']['thumbnails']['maxres']['url']
              caption = f"🎵 Song Name: {title}\n"
              caption += f"🎤 Creator: {creator}\n"
              caption += f"📝 Last updated date: {last_updated_date}\n"
              caption += f"👁 Number of videos: {number_of_videos}\n"

              buttons = InlineKeyboardMarkup(inline_keyboard=[
            [
            InlineKeyboardButton(text='Download MP3', callback_data=f"mpl.{playlist_id}"),
            InlineKeyboardButton(text='Download FLAC', callback_data=f"fpl.{playlist_id}")
            ]
           ])
              await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
              await app.send_photo(message.chat.id, thumb, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'open.spotify.com/track' in final_url:
        parsed_url = urlparse(final_url)
        track_id = parsed_url.path.split('/')[-1]
        track = spoty.get_track(track_id)
        trcknm = track['name']
        img = track['album']['images'][0]['url']
        artist = track['artists'][0]['name']
        fans = track['popularity']
        durations = track['duration_ms'] // 1000
        minutes, seconds = divmod(durations, 60)
        if minutes < 60:
            duration = f"{minutes} minutes {seconds} seconds"
        else:
            duration = f"{minutes // 60} hours {minutes % 60} minutes {seconds} seconds"
        caption = f"🎵 Song Name: {trcknm}\n"
        caption += f"🎤 Artist: {artist}\n"
        caption += f"⏱ Duration: {duration}\n"
        caption += f"👥 Popularity: {fans}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [
            InlineKeyboardButton(text='Download OGG', callback_data=f"ogsp.{track_id}"),
            InlineKeyboardButton(text='Download MP3', callback_data=f"3sp.{track_id}")
            ],
            [InlineKeyboardButton(text='Download FLAC', callback_data=f"fasp.{track_id}")]
        ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, img, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'open.spotify.com/playlist' in final_url:
        parsed_url = urlparse(final_url)
        playlist_id = parsed_url.path.split('/')[-1]
        playlist = spoty.get_playlist(playlist_id)
        duration_ms = sum([track['track']['duration_ms'] for track in playlist['tracks']['items']])
        duration_seconds = duration_ms // 1000
        minutes, seconds = divmod(duration_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            duration_formatted = f"{hours} hours"
        elif minutes > 0:
            duration_formatted = f"{minutes} minutes"
        else:
            duration_formatted = f"{seconds} seconds"
        img = playlist['images'][0]['url']
        title = playlist['name']
        creator = playlist['owner']['display_name']
        caption = f"🎵 Playlist Name: {title}\n"
        caption += f"🎤 Creator: {creator}\n"
        caption += f"👥 Number of tracks: {len(playlist['tracks']['items'])}\n"
        caption += f"⏱ Duration: {duration_formatted}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Download OGG', callback_data=f"playpoo.{playlist_id}"),
                InlineKeyboardButton(text='Download MP3', callback_data=f"ksplay.{playlist_id}")
                ]
            ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, img, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'open.spotify.com/album' in final_url:
        parsed_url = urlparse(final_url)
        album_id = parsed_url.path.split('/')[-1]
        album = spoty.get_album(album_id)
        img = album['images'][0]['url']
        title = album['name']
        creator = album['artists'][0]['name']
        caption = f"📀 Album Name: {title}\n"
        caption += f"👤 Artist: {creator}\n"
        caption += f"👥 Number of tracks: {len(album['tracks']['items'])}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Download OGG', callback_data=f"alsbum.{album_id}"),
                InlineKeyboardButton(text='Download MP3', callback_data=f"flabum.{album_id}")
                ]
            ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, img, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'deezer.com/en/artist' in final_url:
        artist_id = re.findall(r'\d+', clean_url)[-1]
        artist = dez.get_artist(artist_id)
        artist_media = artist.picture_xl
        caption = f"👤 Artist Name: {artist.name}\n"
        caption += f"🎧 Number of albums: {artist.nb_album}\n"
        caption += f"🎵 Number of fans: {artist.nb_fan}\n"
        caption += f"📝 Have Radio: {artist.radio}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text='Download FLAC', callback_data=f"arf.{clean_url}"),
        InlineKeyboardButton(text='Download MP3', callback_data=f"arm.{clean_url}")
        ]
     ])
        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await app.send_photo(message.chat.id, artist_media, caption=caption, reply_markup=buttons, reply_to_message_id=message.id)
     elif 'open.spotify.com/artist' in final_url:
        parsed_url = urlparse(final_url)
        artist_id = parsed_url.path.split('/')[-1]
        artist = sp.artist(artist_id)
        artistmedia = artist['images'][0]['url']
        caption = f"👤 Artist Name: {artist['name']}\n"
        caption += f"🎧 Number of followers: {artist['followers']['total']}\n"
        caption += f"🎵 Number of genres: {len(artist['genres'])}\n"
        caption += f"📝 Popularity: {artist['popularity']}\n"
        buttons = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text='Download OGG', callback_data=f"ggsp.{clean_url}"),
        InlineKeyboardButton(text='Download MP3', callback_data=f"l3hj.{clean_url}")
        ]
     ])
        await app.send_photo(message.chat.id, artistmedia, caption=caption, reply_markup=buttons, reply_to_message_id=message.id) 
     elif 'vt.tiktok.com' and 'vm.tiktok.com' and 'tiktok.com' in final_url:
            meshe = await app.send_message(message.chat.id, 'Recognizing')
            d = snaptik(final_url)
            video_file = f'{userid}.mp4'
            d[0].download(video_file)
            
            # Extract audio from the downloaded video
            video = VideoFileClip(video_file)
            video.audio.write_audiofile(f"{userid}.mp3")
            audio_file = f'{userid}.mp3'
            #Process the extracted audio
            await process_audio_file(audio_file, message, username)
            await meshe.delete()
     elif any(substring in final_url for substring in ['facebook.com', 'x.com']):
            meshe = await app.send_message(message.chat.id, 'Recognizing')
            ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{userid}.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                }

            with ThreadPoolExecutor() as executor:  # Use ThreadPoolExecutor directly
                future = executor.submit(yt_dlp.YoutubeDL(ydl_opts).download, [final_url])
                future.result()
            audio_file = f'{userid}.mp3'

            # Process the downloaded audio
            await process_audio_file(audio_file, message, username)
            await meshe.delete()
     elif 'open.spotify.com/episode' in final_url:
            parsed_url = urllib.parse.urlparse(final_url)
            episode_id = parsed_url.path.split("/")[-1]
            try:
                getinformation = sp.episode(episode_id, market='ID')
                episode_name = getinformation['name']
                thumbnail_url = getinformation['images'][0]['url']
                
                # Download thumbnail image
                thumbnail_filename = os.path.basename(thumbnail_url)
                thumbnail_filepath = os.path.join('./downloads', thumbnail_filename)
                response = requests.get(thumbnail_url)
                with open(thumbnail_filepath, 'wb') as thumbnail_file:
                    thumbnail_file.write(response.content)
                
                # Ensure the thumbnail is in a format accepted by Telegram
                valid_extensions = ['.jpg', '.jpeg', '.png']
                file_extension = os.path.splitext(thumbnail_filename)[1]
                if file_extension not in valid_extensions:
                    converted_thumbnail_filepath = os.path.join('./downloads', os.path.splitext(thumbnail_filename)[0] + '.jpg')
                    img = Image.open(thumbnail_filepath)
                    img.convert('RGB').save(converted_thumbnail_filepath, 'JPEG')
                    thumbnail_filepath = converted_thumbnail_filepath
                
                # Send thumbnail with download options
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Download as OGG", callback_data=f"epsog.{episode_id}")],
                    [InlineKeyboardButton("Download as FLAC", callback_data=f"sepflac.{episode_id}")],
                ])
                caption = f"Title: {episode_name}"
                caption += f"\nPublisher: {getinformation['show']['name']}"
                caption += f"\nRelease Date: {getinformation['release_date']}"
                caption += f"\nDuration: {getinformation['duration_ms'] // 60000} Minutes"
                caption += f"\nDescription: {getinformation['description'][:150]}..."  # Show first 150 characters of description
                await app.send_photo(message.chat.id, photo=thumbnail_filepath, caption=caption, reply_markup=keyboard)
            except Exception as e:
                await send_error_message(app, e)
   except Exception as e:
        await send_error_message(app, e)
 else:
      await ytsearch(client, message)

@app.on_message(filters.sticker | filters.photo | filters.animation)
async def invalid_message(client, message):
        await app.send_message(message.chat.id, 'Give me a link or a song name to search!', reply_to_message_id=message.id)
