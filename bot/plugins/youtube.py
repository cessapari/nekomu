from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import yt_dlp
import re
import asyncio
from bot import app, send_error_message, check_user_id
from bot.utils.utils import resize_image_from_url
import time
from yt_dlp.utils import DownloadError
import requests

downdir = "bot/music/youtube"

def checklenyt(id):
    api_key = "AIzaSyADYQ_f_iYAxHMKL53aORRkLJMd8tOulDU"
    apiurl0 = f"https://www.googleapis.com/youtube/v3/playlists?id={id}&key={api_key}&part=contentDetails"
    apiurl = requests.get(apiurl0)
    rdata = apiurl.json() # Print the entire response
    if 'items' in rdata and rdata['items']:
        video_count = rdata['items'][0]['contentDetails']['itemCount']
        return video_count
      # List to store video details
    
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mpl")))
async def download_playlist(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        url = f"https://www.youtube.com/playlist?list={video_id}"
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Playlist...")
        # Download the audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{downdir}/%(title)s-%(uploader)s.%(ext)s',
            'ignoreerrors': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320'
            }],
        }
        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
         # Take a maximum of `max_tracks` entries # Set the maximum number of tracks based on the user type
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            await asyncio.to_thread(ydl.download, [url])
            max_tracks = 200 if premuser else 60  # Set the maximum number of tracks based on the user type
            if not premuser and len(info_dict['entries']) > 60:
              await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
            elif premuser and len(info_dict['entries']) > 200:
              await app.send_message(callback_query.message.chat.id, "Max Tracks is 200!")
            entries = info_dict['entries'][:max_tracks]  # Take a maximum of `max_tracks` entries

            for entry in entries:
                if entry is None:
                   continue
                try:
                    #ydl.download([entry['webpage_url']])
                    urls = entry['webpage_url']
                    title1 = entry['title']
                    author = entry['uploader']
                    duration = entry['duration']
                    thumbnail = entry['thumbnails'][-1]['url']
                    title = f"{title1}-{author}"
                    mp3_path = os.path.join("bot/music/youtube", f"{title}.mp3")
                    file_size = os.path.getsize(mp3_path) / (1024 * 1024)
                    if not premuser and file_size > 100:
                        await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Upgrade to premium to download large files.")
                        continue
                    elif premuser and file_size > 100:
                        await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Downloading...")
                    # Prepare the thumbnail
                    song_name = title1.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                    thumbnail_name = f"{song_name}_thumbnail"
                    output_path = "bot/music/youtube"
                    thumbnail_file_path = resize_image_from_url(thumbnail, output_path, thumbnail_name)
                    tasks = []
                    titles = title1[:30]
                    arttis = author[:30]
                    reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                    await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                    start = time.time()
                    if os.path.exists(mp3_path):
                        try:
                           task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, audio=mp3_path, title=title, performer=author, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Youtube]({url})", reply_markup=reply_markup))
                           await task
                           tasks.append(task)
                        except ValueError as e:
                            if str(e).startswith("Failed to decode"):
                                print(f"Failed to decode {mp3_path}: {e}")
                                continue
                            raise
                except DownloadError:
                    print(f"Video {urls} is unavailable.")
                    continue
                except Exception as e:
                    print(f"Error downloading or sending audio for {urls}: {e}")
                    continue
            # Delete the audio files
            await asyncio.gather(*tasks)
            await message.delete()
            os.remove(mp3_path)
            os.remove(thumbnail_file_path)
            await app.send_message(callback_query.message.chat.id, f'All song already downloaded! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
        await send_error_message(app, e)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("fpl")))
async def download_playlist(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        url = f"https://www.youtube.com/playlist?list={video_id}"
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Playlist...")
        await app.send_message(callback_query.message.chat.id, "For now, you can only download 10 tracks. Wait till new update at @nekozux!")
        # Download the audio
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{downdir}/%(title)s-%(uploader)s.%(ext)s',
            'ignoreerrors': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
            }],
        }
        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            await asyncio.to_thread(ydl.download, [url])
            max_tracks = 120 if premuser else 10  # Set the maximum number of tracks based on the user type
            if not premuser and len(info_dict['entries']) > 10:
               await app.send_message(callback_query.message.chat.id, "For now, you can only download 10 tracks. Click /info to upgrade your plan!")
            elif premuser and len(info_dict['entries']) > 120:
               await app.send_message(callback_query.message.chat.id, "Max Tracks is 120!")
            entries = info_dict['entries'][:max_tracks]  # Take a maximum of `max_tracks` entries

            for entry in entries:
                if entry is None:
                   continue
                try:
                    #ydl.download([entry['webpage_url']])
                    urls = entry['webpage_url']
                    title1 = entry['title']
                    author = entry['uploader']
                    duration = entry['duration']
                    thumbnail = entry['thumbnails'][-1]['url']
                    title = f"{title1}-{author}"
                    mp3_path = os.path.join("bot/music/youtube", f"{title}.flac")
                    file_size = os.path.getsize(mp3_path) / (1024 * 1024)
                    if not premuser and file_size > 100:
                        await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Upgrade to premium to download large files.")
                        continue
                    elif premuser and file_size > 100:
                        await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Downloading...")
                    # Prepare the thumbnail
                    song_name = title1.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                    thumbnail_name = f"{song_name}_thumbnail"
                    output_path = "bot/music/youtube"
                    thumbnail_file_path = resize_image_from_url(thumbnail, output_path, thumbnail_name)
                    titles = title1[:30]
                    arttis = author[:30]
                    reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                    tasks = []
                    await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                    start = time.time()
                    if os.path.exists(mp3_path):
                        try:
                           task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, audio=mp3_path, title=title, performer=author, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Youtube]({url})", reply_markup=reply_markup))
                           await task
                           tasks.append(task)
                        except ValueError as e:
                            if str(e).startswith("Failed to decode"):
                                print(f"Failed to decode {mp3_path}: {e}")
                                continue
                            raise
                except DownloadError:
                    print(f"Video {urls} is unavailable.")
                    continue
                except Exception as e:
                    print(f"Error downloading or sending audio for {urls}: {e}")
                    continue
            # Delete the audio files
            await asyncio.gather(*tasks)
            await message.delete()
            os.remove(mp3_path)
            os.remove(thumbnail_file_path)
            await app.send_message(callback_query.message.chat.id, f'All song already downloaded! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
        await send_error_message(app, e)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mytb")))
async def download_mp3(client, callback_query):
        # Extract the URL from the callback data
    try:
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Audio...")
        video_id = callback_query.data.split('.', 1)[1]
        url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title1 = info_dict['title']
            author = info_dict['uploader']
            duration = info_dict['duration']
            thumbnail = info_dict['thumbnail']
            title = f"{title1.strip()}-{author.strip()}"

            # Shorten the title if it's too long
            max_length = 100
            if len(title) > max_length:
                title = title[:max_length]

            # Replace any character that is not a letter, number, space, hyphen, or underscore with an underscore
            safe_title = re.sub(r'[^\w\s-]', '_', title)
            # Replace spaces and hyphens with underscores
            safe_title = safe_title.replace(' ', '_').replace('-', '_')
            mp3_path = os.path.join("bot", "music", "youtube", f"{safe_title}")

            # Download the audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': mp3_path + '.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.to_thread(ydl.download, [url]) 
            userid = callback_query.from_user.id
            premuser = check_user_id(userid)
            file_size = os.path.getsize(mp3_path + '.mp3') / (1024 * 1024)  # Get file size in MB
            if not premuser and file_size > 100:
                await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Upgrade to premium to download large files.")
                os.remove(mp3_path + '.mp3')
            elif premuser and file_size > 100:
                await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Downloading...")
            # Prepare the thumbnail
            song_name = title1.replace(" ", "_").replace('-', '_')
            song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
            thumbnail_name = f"{song_name}_thumbnail"
            titles = title1[:30]
            arttis = author[:30]
            reply_markup = InlineKeyboardMarkup(
            [
            [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
            ]
            )
            output_path = os.path.join("bot", "music", "youtube")
            thumbnail_file_path = resize_image_from_url(thumbnail, output_path, thumbnail_name)

            # Send the audio file
            await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
            start = time.time()
            await app.send_audio(callback_query.message.chat.id, audio=mp3_path + '.mp3', title=title, performer=author, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Youtube]({url})", reply_markup=reply_markup)

        await app.send_message(callback_query.message.chat.id, f'All song already downloaded! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        await message.delete()

        # Delete the audio files
        if os.path.exists(mp3_path + '.mp3'):
            os.remove(mp3_path + '.mp3')
    except Exception as e:
        if len(str(e)) > 4096:
            cuted = str(e)[:4096]
            await app.send_message(6627730366, "Error: " + cuted)
        else:
            await app.send_message(6627730366, "Error: " + str(e))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("fytb")))
async def download_fl(client, callback_query):
    try:
        # Extract the URL from the callback data
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Audio...")
        video_id = callback_query.data.split('.', 1)[1]
        url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title1 = info_dict['title']
            author = info_dict['uploader']
            duration = info_dict['duration']
            thumbnail = info_dict['thumbnail']
            title = f"{title1.strip()}-{author.strip()}"

            # Shorten the title if it's too long
            max_length = 50
            if len(title) > max_length:
                title = title[:max_length]

            # Replace any character that is not a letter, number, space, hyphen, or underscore with an underscore
            safe_title = re.sub(r'[^\w\s-]', '_', title)
            # Replace spaces and hyphens with underscores
            safe_title = safe_title.replace(' ', '_').replace('-', '_')
            flac_path = os.path.join("bot", "music", "youtube", f"{safe_title}")

            # Download the audio
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': flac_path + '.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.to_thread(ydl.download, [url]) 
            userid = callback_query.from_user.id
            premuser = check_user_id(userid)
            file_size = os.path.getsize(flac_path + '.flac') / (1024 * 1024)  # Get file size in MB
            if not premuser and file_size > 100:
                await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Upgrade to premium to download large files.")
                os.remove(flac_path + '.flac')
            elif premuser and file_size > 100:
                await app.send_message(callback_query.message.chat.id, "The file size is more than 100MB. Downloading...")
            # Prepare the thumbnail
            song_name = title1.replace(" ", "_").replace('-', '_')
            song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
            thumbnail_name = f"{song_name}_thumbnail"
            output_path = os.path.join("bot", "music", "youtube")
            titles = title1[:30]
            arttis = author[:30]
            reply_markup = InlineKeyboardMarkup(
            [
            [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
            ]
            )
            thumbnail_file_path = resize_image_from_url(thumbnail, output_path, thumbnail_name)

            # Send the audio file
            await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
            await app.send_audio(callback_query.message.chat.id, audio=flac_path + '.flac', title=title, performer=author, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Youtube]({url})", reply_markup=reply_markup)

        await app.send_message(callback_query.message.chat.id, f'All song already downloaded! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        await message.delete()

        # Delete the audio files
        if os.path.exists(flac_path + '.flac'):
            os.remove(flac_path + '.flac')
    except Exception as e:
        if len(str(e)) > 4096:
            cuted = str(e)[:4096]
            await app.send_message(6627730366, "Error: " + cuted)
        else:
            await app.send_message(6627730366, "Error: " + str(e))
            