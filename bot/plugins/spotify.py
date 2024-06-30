from bot import app, spodown, send_error_message, check_user_id
from bot.utils.utils import resize_image_from_url, convert_ogg_to_500kbps, convert_ogg_to_mp3, convert_ogg_to_high_quality_flac
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import fnmatch
import asyncio
import time
from deezloader.spotloader.podcastspo  import PodcastDownloader
from librespot.audio.decoders import AudioQuality

# Set up Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id='70f6025a56d04d8ca55cf9a83596503d', client_secret='4fd4b6de55ae413eac5539a61865815a')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

downdir = "bot/music/spotify"
email='nekozu@gnuweeb.org'
pwd='Farih2009@'

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("ogsp")))
async def download_oggsp(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        spot = sp.track(video_id)
        title = spot['name']
        song_name = title.replace(" ", "_")
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  

        song_path = os.path.join("bot/music/spotify", f"{song_name}.ogg")

        
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Audio...")
        spoty_url = spot['external_urls']['spotify'] # Access URL
        down = await asyncio.to_thread(spodown.download_track, spoty_url, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False,  output_dir=downdir)
        await asyncio.to_thread(convert_ogg_to_500kbps, down.song_path, song_path)
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Lyrics", callback_data="lyrics.{}")]
            ]
        )
        # Send the audio file
        duration = spot['duration_ms'] // 1000
        urlimg = spot['album']['images'][0]['url']
        artist = spot['artists'][0]['name']# Corrected line
        song_name = title.replace(" ", "_")
        titles = title[:30]
        arttis = artist[:30]
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
            ]
        )
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
        thumbnail_name = f"{song_name}_thumbnail"
        output_path = "bot/music/spotify"
        thumbnail_file_path = await asyncio.to_thread(resize_image_from_url, urlimg, output_path, thumbnail_name)
        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
        start = time.time()
        await app.send_audio(callback_query.message.chat.id, audio=song_path, title=title, performer=artist, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Spotify]({spoty_url}", reply_markup=reply_markup)
        await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        os.remove(song_path)
        os.remove(thumbnail_file_path)
        os.remove(down.song_path)
        await message.delete()
    except Exception as e:
     await send_error_message(app, e)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("fasp")))
async def download_flacsp(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        spot = sp.track(video_id)
        title = spot['name']
        song_name = title.replace(" ", "_")
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  

        song_path = os.path.join("bot/music/spotify", f"{song_name}.flac")

        
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Audio...")
        spoty_url = spot['external_urls']['spotify'] # Access URL
        down = await asyncio.to_thread(spodown.download_track, spoty_url, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False,  output_dir=downdir)
        await asyncio.to_thread(convert_ogg_to_high_quality_flac, down.song_path, song_path)

        # Send the audio file
        duration = spot['duration_ms'] // 1000
        urlimg = spot['album']['images'][0]['url']
        artist = spot['artists'][0]['name']# Corrected line
        song_name = title.replace(" ", "_")
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
        thumbnail_name = f"{song_name}_thumbnail"
        titles = title[:30]
        arttis = artist[:30]
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
            ]
        )
        output_path = "bot/music/spotify"
        thumbnail_file_path = await asyncio.to_thread(resize_image_from_url, urlimg, output_path, thumbnail_name)
        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
        start = time.time()
        await app.send_audio(callback_query.message.chat.id, audio=song_path, title=title, performer=artist, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Spotify]({spoty_url})", reply_markup=reply_markup)
        await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        os.remove(thumbnail_file_path)
        os.remove(down.song_path)
        os.remove(song_path)
        await message.delete()
    except Exception as e:
     await send_error_message(app, callback_query.message.chat.id, e)
     await app.send_message(callback_query.message.chat.id, f"An error occurred, Maybe your link invalid or the track is unavailable or cannot downloaded because copyright. Try another link!")
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("3sp")))
async def download_mp3sp(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        spot = sp.track(video_id)
        title = spot['name']
        song_name = title.replace(" ", "_")
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  

        song_path = os.path.join("bot/music/spotify", f"{song_name}.mp3")
        
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Audio...")
        spoty_url = spot['external_urls']['spotify'] # Access URL
        down = await asyncio.to_thread(spodown.download_track, spoty_url, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False,  output_dir=downdir)
        await asyncio.to_thread(convert_ogg_to_mp3, down.song_path, song_path)

        # Send the audio file
        duration = spot['duration_ms'] // 1000
        urlimg = spot['album']['images'][0]['url']
        artist = spot['artists'][0]['name']# Corrected line
        song_name = title.replace(" ", "_")
        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
        thumbnail_name = f"{song_name}_thumbnail"
        titles = title[:30]
        arttis = artist[:30]
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
            ]
        )
        output_path = "bot/music/spotify"
        thumbnail_file_path = await asyncio.to_thread(resize_image_from_url, urlimg, output_path, thumbnail_name)
        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
        start = time.time()
        await app.send_audio(callback_query.message.chat.id, audio=song_path, title=title, performer=artist, duration=duration, thumb=thumbnail_file_path, caption=f"🔗 [Spotify]({spoty_url})", reply_markup=reply_markup)
        await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        await message.delete()
        os.remove(song_path)
        os.remove(thumbnail_file_path)
        os.remove(down.song_path)
    except Exception as e:
     await send_error_message(app, callback_query.message.chat.id, e)
     await app.send_message(callback_query.message.chat.id, f"An error occurred, Maybe your link invalid or the track is unavailable or cannot downloaded because copyright. Try another link!")

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("playpoo")))
async def downloadplaylistoggsp(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        spot = sp.playlist(video_id)
        tracks = spot['tracks']['items']
        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Playlist...")

        tasks = []
        audio_files = []  # Initialize audio_files here

        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
        if premuser == False:
            if len(tracks) > 40:
               await app.send_message(callback_query.message.chat.id, "For now, you can only download 40 tracks. Click /info to upgrade your plan!")
               tracks = tracks[:40]
        else:
            if len(tracks) > 140:
                await app.send_message(callback_query.message.chat.id, "Max is 140 tracks")
                tracks = tracks[:140]
                
        for track in tracks:
                spoty_url = None  # Initialize spoty_url
                try:
                        spoty_url = track['track']['external_urls']['spotify']  # Access URL
                        title = track['track']['name']  # Get the track name
                        song_name = title.replace(" ", "_")
                        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                        song_path = os.path.join("bot/music/spotify", f"{song_name}.ogg")
                        down = await asyncio.to_thread(spodown.download_track, spoty_url, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False,  output_dir=downdir)
                        await asyncio.to_thread(convert_ogg_to_500kbps, down.song_path, song_path)
                        print(down.song_path)

                        duration = track['track']['duration_ms'] // 1000
                        urlimg = track['track']['album']['images'][0]['url']
                        artist = track['track']['artists'][0]['name'] # Corrected line
                        song_name = title.replace(" ", "_")
                        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                        thumbnail_name = f"{song_name}_thumbnail"
                        output_path = "bot/music/spotify"
                        titles = title[:30]
                        arttis = artist[:30]
                        reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                        thumbnail_file_path = await asyncio.to_thread(resize_image_from_url, urlimg, output_path, thumbnail_name)
                        
                        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)

                        # Get a list of all audio files that match the song name
                        audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.ogg")

                        for audio_file in audio_files:
                            audio_path = os.path.join("bot/music/spotify", audio_file)
                            start = time.time()
                            if os.path.exists(audio_path):  # Check if the file exists
                                task = asyncio.create_task(
                                app.send_audio(
                                    callback_query.message.chat.id, 
                                    audio=audio_path, 
                                    title=title,  # Use the track name as the title
                                    performer=artist, 
                                    duration=duration, 
                                    thumb=thumbnail_file_path,
                                    caption=f"🔗 [Spotify]({spoty_url})",
                                    disable_notification=True,
                                    reply_markup=reply_markup
                                )
                            )
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                        for audio_file in audio_files:
                            audio_path = os.path.join("bot/music/spotify", audio_file)
                            os.remove(audio_path)
                            os.remove(down.song_path)
                            os.remove(thumbnail_file_path)
                            await message.delete()
                except Exception as e:
                        error_message = f"Error downloading or converting track from URL: {spoty_url if spoty_url else 'Unknown URL'}"
                        print(error_message)
                        await send_error_message(app, message.message.chat.id, e)
                        continue
        await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
        # Wait for all tasks to complete
    except Exception as e:
     await send_error_message(app, e)
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("ksplay")))
async def downloadplaylistmp3sp(client, callback_query):
    try:
            video_id = callback_query.data.split('.', 1)[1]
            spot = sp.playlist(video_id)
            tracks = spot['tracks']['items']
            message = await app.send_message(callback_query.message.chat.id, "Downloading Your Playlist...")

            tasks = []
            audio_files = []

            userid = callback_query.from_user.id
            premuser = check_user_id(userid)
            if premuser == False:
              if len(tracks) > 60:
                await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
                tracks = tracks[:60]
            else:
              if len(tracks) > 200:
                await app.send_message(callback_query.message.chat.id, "Max is 200 tracks")
                tracks = tracks[:200]

            for track in tracks:
                    spoty_url = None  # Initialize spoty_url
                    try:
                        spoty_url = track['track']['external_urls']['spotify']  # Access URL
                        title = track['track']['name']  # Get the track name
                        song_name = title.replace(" ", "_")
                        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                        song_path = os.path.join("bot/music/spotify", f"{song_name}.mp3")
                        down_task = asyncio.to_thread(spodown.download_track, spoty_url, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False,  output_dir=downdir)
                        down = await down_task
                        convert_task = asyncio.to_thread(convert_ogg_to_mp3, down.song_path, song_path)
                        await convert_task
                        print(down.song_path)

                        duration = track['track']['duration_ms'] // 1000
                        urlimg = track['track']['album']['images'][0]['url']
                        artist = track['track']['artists'][0]['name'] # Corrected line
                        song_name = title.replace(" ", "_")
                        song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                        thumbnail_name = f"{song_name}_thumbnail"
                        titles = title[:30]
                        arttis = artist[:30]
                        reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                        output_path = "bot/music/spotify"
                        thumbnail_task = asyncio.to_thread(resize_image_from_url, urlimg, output_path, thumbnail_name)
                        thumbnail_file_path = await thumbnail_task
                        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)

                    # Get a list of all audio files that match the song name
                        audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.mp3")

                        for audio_file in audio_files:
                             audio_path = os.path.join("bot/music/spotify", audio_file)
                             if os.path.exists(audio_path):  # Check if the file exists
                                task = asyncio.create_task(
                                app.send_audio(
                                callback_query.message.chat.id, 
                                audio=audio_path, 
                                title=title,  # Use the track name as the title
                                performer=artist, 
                                duration=duration, 
                                thumb=thumbnail_file_path,
                                caption=f"🔗 [Spotify]({spoty_url})",
                                disable_notification=True,
                                reply_markup=reply_markup
                            )
                        )
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                        for audio_file in audio_files:
                            audio_path = os.path.join("bot/music/spotify", audio_file)
                            os.remove(audio_path)
                            os.remove(down.song_path)
                            os.remove(thumbnail_file_path)
                            await message.delete()
                    except Exception as e:
                        error_message = f"Error downloading or converting track from URL: {spoty_url if spoty_url else 'Unknown URL'}"
                        print(error_message)
                        print(e)
                        continue
            await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
     await send_error_message(app, e)
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("alsbum")))
async def downalbumoggsp(client, callback_query):
    try:
            video_id = callback_query.data.split('.', 1)[1]
            album = sp.album(video_id)
            tracks = album['tracks']['items']
            
            message = await app.send_message(callback_query.message.chat.id, "Downloading Your Album...")

            userid = callback_query.from_user.id
            premuser = check_user_id(userid)
            if premuser == False:
                if len(tracks) > 40:
                  await app.send_message(callback_query.message.chat.id, "For now, you can only download 40 tracks. Click /info to upgrade your plan!")
                  tracks = tracks[:40]
            else:
                if len(tracks) > 140:
                   await app.send_message(callback_query.message.chat.id, "Max is 140 tracks")
                   tracks = tracks[:140]

            tasks = []
            for track in tracks:
                trackurl = None
                #thumbnail_file_path = None# Initialize spoty_url
                try:
                    trackurl = track['external_urls']['spotify']  # Access URL
                    title = track['name']  # Corrected line
                    artist_name = track['artists'][0]['name']
                    artist_name = re.sub(r'[\\/*?:"<>|]',"", artist_name)
                    song_name = re.sub(r'[\\/*?:"<>|]',"", title)
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                    song_path = os.path.join("bot/music/spotify", f"{song_name}.ogg")
                    down_task = asyncio.to_thread(spodown.download_track, trackurl, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False, output_dir=downdir)
                    down = await down_task
                    convert_task = asyncio.to_thread(convert_ogg_to_500kbps, down.song_path, song_path)
                    await convert_task
                    print(down.song_path)

                    duration = track['duration_ms'] // 1000
                    artist = track['artists'][0]['name']
                    imgurl = album['images'][0]['url']  # Assuming correct dictionary structure# Corrected line
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                    thumbnail_name = f"{song_name}_thumbnail"
                    output_path = "bot/music/spotify"
                    thumbnail_task = asyncio.to_thread(resize_image_from_url, imgurl, output_path, thumbnail_name)
                    thumbnail_file_path = await thumbnail_task
                    await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)

                    # Get a list of all audio files that match the song name
                    titles = title[:30]
                    arttis = artist[:30]
                    reply_markup = InlineKeyboardMarkup(
                    [
                    [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                    ]
                    )
                    audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.ogg")

                    for audio_file in audio_files:
                        audio_path = os.path.join("bot/music/spotify", audio_file)
                        start = time.time()
                        if os.path.exists(audio_path):  # Check if the file exists
                            task = asyncio.create_task(
                            app.send_audio(
                                callback_query.message.chat.id, 
                                audio=audio_path, 
                                title=title,  # Use the track name as the title
                                performer=artist, 
                                duration=duration, 
                                thumb=thumbnail_file_path,
                                caption=f"🔗 [Spotify]({trackurl})",
                                disable_notification=True,
                                reply_markup=reply_markup
                            )
                        )
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                        for audio_file in audio_files:
                            audio_path = os.path.join("bot/music/spotify", audio_file)
                            os.remove(audio_path)
                            os.remove(down.song_path)
                            os.remove(thumbnail_file_path)
                            await message.delete()
                except Exception as e:
                    error_message = f"Error downloading or converting track from URL: {trackurl if trackurl else 'Unknown URL'}"
                    print(error_message)
                    print(e)
                    continue
            await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
     await send_error_message(app, e)
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flabum")))
async def downalbummp3sp(client, callback_query):
    try:
        video_id = callback_query.data.split('.', 1)[1]
        album = sp.album(video_id)
        tracks = album['tracks']['items']

        message = await app.send_message(callback_query.message.chat.id, "Downloading Your Album...")

        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
        if premuser == False:
            if len(tracks) > 60:
                await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
                tracks = tracks[:60]
        else:
            if len(tracks) > 200:
                await app.send_message(callback_query.message.chat.id, "Max is 200 tracks")
                tracks = tracks[:200]

        tasks = []
        for track in tracks:
            trackurl = None
            thumbnail_file_path = None# Initialize spoty_url
            try:
                trackurl = track['external_urls']['spotify']  # Access URL
                title = track['name']  # Corrected line
                artist_name = track['artists'][0]['name']
                artist_name = re.sub(r'[\\/*?:"<>|]',"", artist_name)
                song_name = re.sub(r'[\\/*?:"<>|]',"", title)
                song_name = title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                song_path = os.path.join("bot/music/spotify", f"{song_name}.mp3")
                down_task = asyncio.to_thread(spodown.download_track, trackurl, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False, output_dir=downdir)
                down = await down_task
                convert_task = asyncio.to_thread(convert_ogg_to_mp3, down.song_path, song_path)
                await convert_task
                print(down.song_path)

                duration = track['duration_ms'] // 1000 
                artist = track['artists'][0]['name']
                imgurl = album['images'][0]['url']  # Assuming correct dictionary structure # Corrected line
                song_name = title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                thumbnail_name = f"{song_name}_thumbnail"
                output_path = "bot/music/spotify"
                thumbnail_task = asyncio.to_thread(resize_image_from_url, imgurl, output_path, thumbnail_name)
                thumbnail_file_path = await thumbnail_task
                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)

                # Get a list of all audio files that match the song name
                titles = title[:30]
                arttis = artist[:30]
                reply_markup = InlineKeyboardMarkup(
                [
                [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                ]
                )
                audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.mp3")

                for audio_file in audio_files:
                    audio_path = os.path.join("bot/music/spotify", audio_file)
                    if os.path.exists(audio_path):  # Check if the file exists
                        task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=title,  # Use the track name as the title
                            performer=artist, 
                            duration=duration, 
                            thumb=thumbnail_file_path,
                            caption=f"🔗 [Spotify]({trackurl})", 
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    await asyncio.gather(*tasks)
                    for audio_file in audio_files:
                            audio_path = os.path.join("bot/music/spotify", audio_file)
                            os.remove(audio_path)
                            os.remove(down.song_path)
                            os.remove(thumbnail_file_path)
                            await message.delete()
            except Exception as e:
                    error_message = f"Error downloading or converting track from URL: {trackurl if trackurl else 'Unknown URL'}"
                    print(error_message)
                    print(e)
                    continue
        await app.send_message(callback_query.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
     await send_error_message(app, e)
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("ggsp")))
async def diownoggart(client, message):
    try:
        artist_id = message.data.split('.', 1)[1]
        artist_albums = sp.artist_albums(artist_id)
        messages = await app.send_message(message.message.chat.id, "Downloading Your Artist Tracks...")

        userid = message.from_user.id
        premuser = check_user_id(userid)
        if premuser == False:
            if len(artist_albums['items']) > 40:
                await app.send_message(message.message.chat.id, "For now, you can only download 40 tracks. Click /info to upgrade your plan!")
                artist_albums['items'] = artist_albums['items'][:40]
        else:
            if len(artist_albums['items']) > 140:
                await app.send_message(message.message.chat.id, "Max is 140 tracks")
                artist_albums['items'] = artist_albums['items'][:140]

        tasks = []
        for album in artist_albums['items']:
            album_tracks = sp.album_tracks(album['id'])
            for track in album_tracks['items']:
                trackurl = None
                thumbnail_file_path = None
                try:
                    trackurl = track['external_urls']['spotify']  # Access URL
                    title = track['name']  # Corrected line
                    artist_name = track['artists'][0]['name']
                    artist_name = re.sub(r'[\\/*?:"<>|]',"",artist_name)
                    song_name = re.sub(r'[\\/*?:"<>|]',"",title)
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                    song_path = os.path.join("bot/music/spotify", f"{song_name}.ogg")
                    down = spodown.download_track(trackurl, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False, output_dir=downdir)
                    convert_ogg_to_500kbps(down.song_path, song_path)
                    print(down.song_path)

                    duration = track['duration_ms'] // 1000
                    artist = track['artists'][0]['name']
                    imgurl = album['images'][0]['url']  # Assuming correct dictionary structure # Corrected line
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                    thumbnail_name = f"{song_name}_thumbnail"
                    titles = title[:30]
                    arttis = artist[:30]
                    reply_markup = InlineKeyboardMarkup(
                    [
                    [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                    ]
                    )
                    output_path = "bot/music/spotify"
                    thumbnail_file_path = resize_image_from_url(imgurl, output_path, thumbnail_name)
                    await app.send_chat_action(message.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                    audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.ogg")
                    for audio_file in audio_files:
                        audio_path = os.path.join("bot/music/spotify", audio_file)
                        if os.path.exists(audio_path):
                            task = asyncio.create_task(
                            app.send_audio(
                                message.message.chat.id, 
                                audio=audio_path, 
                                title=title,  # Use the track name as the title
                                performer=artist, 
                                duration=duration, 
                                thumb=thumbnail_file_path,
                                caption=f"🔗 [Spotify]({trackurl})",
                                disable_notification=True,
                                reply_markup=reply_markup
                            )
                        )
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                        for audio_file in audio_files:
                                audio_path = os.path.join("bot/music/spotify", audio_file)
                                os.remove(audio_path)
                                os.remove(down.song_path)
                                os.remove(thumbnail_file_path)
                                await messages.delete()
                except Exception as e:
                    error_message = f"Error downloading or converting track from URL: {trackurl if trackurl else 'Unknown URL'}"
                    print(error_message)
                    print(e)
                    continue
        await app.send_message(message.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
        error_message = str(e)
        if len(error_message) > 50:
            error_message = error_message[:50] + '...'
        await app.send_message(message.message.chat.id, f"An error occurred: {error_message}, Maybe your link invalid or the track is unavailable or cannot downloaded because of the artist is unavailable. Try another link!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Send Error to admin", callback_data=f"e.{error_message}")]]))
        
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("l3hj")))
async def downomp3art(client, message):
    try:
        artist_id = message.data.split('.', 1)[1]
        artist_albums = sp.artist_albums(artist_id)
        messages = await app.send_message(message.message.chat.id, "Downloading Your Artist Tracks...")

        userid = message.from_user.id
        premuser = check_user_id(userid)
        if premuser == False:
            if len(artist_albums['items']) > 60:
                await app.send_message(message.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
                artist_albums['items'] = artist_albums['items'][:60]
        else:
            if len(artist_albums['items']) > 200:
                await app.send_message(message.message.chat.id, "Max is 200 tracks")
                artist_albums['items'] = artist_albums['items'][:200]

        tasks = []
        for album in artist_albums['items']:
            album_tracks = sp.album_tracks(album['id'])
            for track in album_tracks['items']:
                trackurl = None
                thumbnail_file_path = None
                try:
                    trackurl = track['external_urls']['spotify']  # Access URL
                    title = track['name']  # Corrected line
                    artist_name = track['artists'][0]['name']
                    artist_name = re.sub(r'[\\/*?:"<>|]',"",artist_name)
                    song_name = re.sub(r'[\\/*?:"<>|]',"",title)
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                    song_path = os.path.join("bot/music/spotify", f"{song_name}.mp3")  # Change the extension to .mp3
                    down = spodown.download_track(trackurl, quality_download='NORMAL', recursive_quality=True, recursive_download=True, not_interface=True, method_save=2, is_thread=False, output_dir=downdir)
                    convert_ogg_to_mp3(down.song_path, song_path)  # Use convert_ogg_to_mp3 function

                    duration = track['duration_ms'] // 1000
                    artist = track['artists'][0]['name']
                    imgurl = album['images'][0]['url']  # Assuming correct dictionary structure # Corrected line
                    song_name = title.replace(" ", "_")
                    song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                    thumbnail_name = f"{song_name}_thumbnail"
                    output_path = "bot/music/spotify"
                    titles = title[:30]
                    arttis = artist[:30]
                    reply_markup = InlineKeyboardMarkup(
                    [
                    [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                    ]
                    )
                    thumbnail_file_path = resize_image_from_url(imgurl, output_path, thumbnail_name)
                    await app.send_chat_action(message.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                    audio_files = fnmatch.filter(os.listdir("bot/music/spotify"), f"*{song_name}*.mp3")  # Change the extension to .mp3
                    for audio_file in audio_files:
                        audio_path = os.path.join("bot/music/spotify", audio_file)
                        if os.path.exists(audio_path):
                            task = asyncio.create_task(
                            app.send_audio(
                                message.message.chat.id, 
                                audio=audio_path, 
                                title=title,  # Use the track name as the title
                                performer=artist, 
                                duration=duration, 
                                thumb=thumbnail_file_path,
                                caption=f"🔗 [Spotify]({trackurl})",
                                disable_notification=True,
                                reply_markup=reply_markup
                            )
                        )
                        tasks.append(task)
                        await asyncio.gather(*tasks)
                        for audio_file in audio_files:
                                audio_path = os.path.join("bot/music/spotify", audio_file)
                                os.remove(audio_path)
                                os.remove(down.song_path)
                                os.remove(thumbnail_file_path)
                                await messages.delete()
                except Exception as e:
                    error_message = f"Error downloading or converting track from URL: {trackurl if trackurl else 'Unknown URL'}"
                    print(error_message)
                    print(e)
                    continue
        await app.send_message(message.message.chat.id, f'Song sent! Dont forget to subs below!', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]))
    except Exception as e:
        error_message = str(e)
        if len(error_message) > 50:
            error_message = error_message[:50] + '...'
        await app.send_message(message.message.chat.id, f"An error occurred: {error_message}, Maybe your link invalid or the track is unavailable or cannot downloaded because of the artist is unavailable. Try another link!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Send Error to admin", callback_data=f"e.{error_message}")]]))
     
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("epsog")))
async def download_episode_ogg(client, callback_query):
    episode_id = callback_query.data.split('.')[-1]
    messages = await app.send_message(callback_query.message.chat.id, "Downloading MP3 Episode")
    try:
        episode_info = sp.episode(episode_id, market='ID')
        episode_url = f"spotify:episode:{episode_id}"
        downdown = PodcastDownloader(email, pwd, episode_url, AudioQuality.NORMAL, 'bot/music/spotify')
        ogg_file = await asyncio.to_thread(downdown.download_episode)
        await app.send_message(callback_query.message.chat.id, "Downloading episode in OGG format...")
        
        # Convert thumbnail
        thumbnail_url = episode_info['images'][0]['url']
        thumbnail_path = await asyncio.to_thread(resize_image_from_url, thumbnail_url, './downloads', f"{episode_id}_thumbnail")
        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
        
        if episode_info['duration_ms'] // 60000 > 30 and not premuser:
            await app.send_message(callback_query.message.chat.id, "This episode is longer than 30 minutes and requires to be premium to listen.")
        else:
            await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
            send_task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, audio=ogg_file, title=episode_info['name'], performer=episode_info['show']['publisher'], duration=episode_info['duration_ms'] // 1000, thumb=thumbnail_path, caption=f"🔗 [Spotify]({episode_info['external_urls']['spotify']})"))
            await asyncio.gather(send_task)
            os.remove(ogg_file)
            os.remove(thumbnail_path)
            await messages.delete()
    except Exception as e:
        await send_error_message(app, e)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("sepflac")))
async def download_episode_flac(client, callback_query):
    episode_id = callback_query.data.split('.')[-1]
    messages = await app.send_message(callback_query.message.chat.id, "Downloading FLAC Episode")
    try:
        episode_info = sp.episode(episode_id, market='ID')
        userid = callback_query.from_user.id
        premuser = check_user_id(userid)
        if not premuser:
            await app.send_message(callback_query.message.chat.id, "This episode format is only available on a premium account to download in FLAC quality.")
            return
        episode_url = f"spotify:episode:{episode_id}"
        downdown = PodcastDownloader(email, pwd, episode_url, AudioQuality.NORMAL, 'bot/music/spotify')
        ogg_file_path = await asyncio.to_thread(downdown.download_episode)
        flac_path = os.path.join('bot/music/spotify', f'{episode_id}.flac')
        flac_data = await asyncio.to_thread(convert_ogg_to_high_quality_flac, ogg_file_path, flac_path)
        if flac_data is None:
            await send_error_message(app, "Failed to convert OGG to FLAC.")
            return
        # Write FLAC data to a temporary file
        temp_dir = 'bot/music/spotify'
        temp_flac_file = os.path.join(temp_dir, f"{episode_id}.flac")
        # Convert thumbnail
        thumbnail_url = episode_info['images'][0]['url']
        thumbnail_dir = './downloads'
        thumbnail_path = await asyncio.to_thread(resize_image_from_url, thumbnail_url, thumbnail_dir, f"{episode_id}_thumbnail")
        await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
        send_task = asyncio.create_task(app.send_audio(callback_query.message.chat.id, audio=temp_flac_file, title=episode_info['name'], performer=episode_info['show']['publisher'], duration=episode_info['duration_ms'] // 1000, thumb=thumbnail_path, caption=f"🔗 [Spotify]({episode_info['external_urls']['spotify']})"))
        await asyncio.gather(send_task)
        os.remove(ogg_file_path)
        os.remove(temp_flac_file)
        os.remove(flac_data)
        os.remove(thumbnail_path)
        await messages.delete()
    except Exception as e:
        await send_error_message(app, e)

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("e")))
async def error_send(_, callback_query):
    error = callback_query.data.split(".")
    await app.send_message(6985853898, f"An error occurred: {error[1]}")

