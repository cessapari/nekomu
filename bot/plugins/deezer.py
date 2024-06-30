from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import app, dez, downloa, deezer, check_user_id
import time
import re
import os
import asyncio
import json
from bot.utils.utils import progress, convert_mp3_to_flac, resize_image_from_url

downdir = './bot/music/deezer'

async def download_song_flac(track):
        api = track['SNG_ID']
        url = f"https://deezer.com/en/track/{api}"

        # Download the song as MP3 using the existing function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        mp3_path = down.song_path

        # Convert the downloaded MP3 to FLAC
        flac_bytes = convert_mp3_to_flac(mp3_path)

        # Save the FLAC file to disk
        flac_path = mp3_path.replace('.mp3', '.flac')
        with open(flac_path, 'wb') as flac_file:
            flac_file.write(flac_bytes)
        try:
           os.remove(mp3_path)
        except OSError as e:
            print(e)

        return flac_path
    
async def download_song_flac_art(track):
        api = track.id
        url = f"https://deezer.com/en/track/{api}"

        # Download the song as MP3 using the existing function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        mp3_path = down.song_path

        # Convert the downloaded MP3 to FLAC
        flac_bytes = convert_mp3_to_flac(mp3_path)

        # Save the FLAC file to disk
        flac_path = mp3_path.replace('.mp3', '.flac')
        with open(flac_path, 'wb') as flac_file:
            flac_file.write(flac_bytes)
        try:
           os.remove(mp3_path)
        except OSError as e:
            print(e)

        return flac_path
    
async def download_song_flac_trck(track):
        api = track.id
        url = f"https://deezer.com/en/track/{api}"

        # Download the song as MP3 using the existing function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        mp3_path = down.song_path

        # Convert the downloaded MP3 to FLAC
        flac_bytes = convert_mp3_to_flac(mp3_path)

        # Save the FLAC file to disk
        flac_path = mp3_path.replace('.mp3', '.flac')
        with open(flac_path, 'wb') as flac_file:
            flac_file.write(flac_bytes)
        try:
           os.remove(mp3_path)
        except OSError as e:
            print(e)

        return flac_path
    
async def download_song_mp3_trck(track):
        api = track.id
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path

async def download_song_mp3(track):
        api = track['SNG_ID']
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path

async def download_song_mp3_art(track):
        api = track.id
        url = f"https://deezer.com/en/track/{api}"
        # run the blocking download function
        down = downloa.download_trackdee(url, output_dir=downdir, quality_download='MP3_128', recursive_download=True, recursive_quality=True, not_interface=True, method_save=2)
        print(down.song_path)
        return down.song_path

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flacpl")))
async def download_flac_playlist(_, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading Your FLAC Playlist...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_playlist_tracks(playlist_id)

    # Check if the user is premium
    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)
    if not premiumornot:
        if len(playlist_tracks) > 10:
            await app.send_message(callback_query.message.chat.id, "For now, you can only download 10 tracks. Click /info to upgrade your plan!")
            playlist_tracks = playlist_tracks[:10]
    else:
        if len(playlist_tracks) > 120:
            await app.send_message(callback_query.message.chat.id, "Max Tracks is 120!")
            playlist_tracks = playlist_tracks[:120]

    tasks = []
    flac_file_paths = []  # Store FLAC paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in playlist_tracks:
        try:
            flac_path = await download_song_flac(track)  # Download FLAC
            if flac_path is not None and flac_path:  # Check if download successful
                e = dez.get_track(track['SNG_ID'])
                minutes, seconds = divmod(e.duration, 60)

                song_name = e.title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # Remove invalid characters

                pict = dez.get_track(track['SNG_ID'])
                playlist_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(playlist_thumbnail, downdir, song_name)
                titles = e.title[:30]
                arttis = e.artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )

                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                
                if os.path.exists(flac_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=flac_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track['SNG_ID']})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    flac_file_paths.append(flac_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(flac_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {flac_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track['SNG_ID']}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))
    
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flacal")))
async def download_flac_album(_, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading Your FLAC Album...")
    track_parts = callback_query.data.split(".")
    album_url = ".".join(track_parts[1:])
    album_id = int(album_url.split('/')[-1])
    album_tracks = deezer.get_album_tracks(album_id)

    # Check if the user is premium
    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)
    if not premiumornot:
        if len(album_tracks) > 10:
            await app.send_message(callback_query.message.chat.id, "For now, you can only download 10 tracks. Click /info to upgrade your plan!")
            album_tracks = album_tracks[:10]
    else:
        if len(album_tracks) > 120:
            await app.send_message(callback_query.message.chat.id, "Max Tracks is 120!")
            album_tracks = album_tracks[:120]

    tasks = []
    flac_file_paths = []  # Store FLAC paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in album_tracks:
        try:
            flac_path = await download_song_flac(track)  # Download FLAC
            if flac_path is not None:  # Check if download successful
                e = dez.get_track(track['SNG_ID'])
                minutes, seconds = divmod(e.duration, 60)

                song_name = e.title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # Remove invalid characters

                pict = dez.get_track(track['SNG_ID'])
                album_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(album_thumbnail, downdir, song_name)
                titles = e.title[:30]
                arttis = e.artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )

                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                
                audio_path = str(flac_path)
                if os.path.exists(audio_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track['SNG_ID']})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    flac_file_paths.append(flac_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(flac_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {audio_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track['SNG_ID']}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3pl")))
async def download_mp3_playlist(_, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading Your MP3 Playlist...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_playlist_tracks(playlist_id)
    tasks = []

    # Check if the user is premium
    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)
    if premiumornot == False:
        if len(playlist_tracks) > 60:
            await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
            playlist_tracks = playlist_tracks[:60]
    else:
        if len(playlist_tracks) > 200:
            await app.send_message(callback_query.message.chat.id, "Max Tracks is 200!")
            playlist_tracks = playlist_tracks[:200]

    tasks = []
    mp3_file_paths = []  # Store MP3 paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in playlist_tracks:
        try:
            mp3_path = await download_song_mp3(track)  # Download MP3
            if mp3_path is not None:  # Check if download successful
                e = dez.get_track(track['SNG_ID'])
                song_name = e.title.replace(" ", "_")
                pict = dez.get_track(track['SNG_ID'])
                playlist_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(playlist_thumbnail, downdir, song_name)
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                titles = e.title[:30]
                arttis = e.artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                audio_path = str(mp3_path)
                if os.path.exists(audio_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track['SNG_ID']})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    mp3_file_paths.append(mp3_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(mp3_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {audio_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track['SNG_ID']}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3al")))
async def download_mp3_album(_, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading Your MP3 Album...")
    track_parts = callback_query.data.split(".")
    playlist_url = ".".join(track_parts[1:])
    playlist_id = int(playlist_url.split('/')[-1])
    playlist_tracks = deezer.get_album_tracks(playlist_id)
    tasks = []

    # Check if the user is premium
    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)
    if premiumornot == False:
        if len(playlist_tracks) > 60:
            await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
            playlist_tracks = playlist_tracks[:60]
    else:
        if len(playlist_tracks) > 200:
            await app.send_message(callback_query.message.chat.id, "Max Tracks is 200!")
            playlist_tracks = playlist_tracks[:200]

    tasks = []
    mp3_file_paths = []  # Store MP3 paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in playlist_tracks:
        try:
            mp3_path = await download_song_mp3(track)  # Download MP3
            if mp3_path is not None:  # Check if download successful
                e = dez.get_track(track['SNG_ID'])
                song_name = e.title.replace(" ", "_")
                pict = dez.get_track(track['SNG_ID'])
                playlist_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(playlist_thumbnail, downdir, song_name)
                titles = e.title[:30]
                arttis = e.artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                audio_path = str(mp3_path)
                if os.path.exists(audio_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track['SNG_ID']})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    mp3_file_paths.append(mp3_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(mp3_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {audio_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track['SNG_ID']}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("flac")))
async def downdezfl(client, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading FLAC...")
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])  # Join all parts except the first one
    track_id = track_url.split('/')[-1]  # Extract the track ID from the URL
    track = dez.get_track(track_id)  # Pass the track ID to get_track
    tracks = [track]  # Put the track into a list

    for track in tracks:
            # Schedule download_song to run in the executor
        flac_path = await download_song_flac_trck(track)
        e = dez.get_track(track.id)

        if flac_path is not None:
            song_name = e.title.replace(" ", "_")
            pict = dez.get_track(track.id)
            playlist_thumbnail = pict.album.cover_small
            thumbnail_file_path = resize_image_from_url(playlist_thumbnail, downdir, song_name)
            song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  
            titles = e.title[:30]
            arttis = e.artist.name[:30]
            reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
            await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
            start = time.time()
            await app.send_audio(callback_query.message.chat.id, audio=flac_path, title=e.title, performer=e.artist.name, duration=e.duration, thumb=thumbnail_file_path, caption=f"🔗 [Deezer](https://deezer.com/en/track/{track.id})", reply_markup=reply_markup)           

    await message.delete()
    if os.path.exists(flac_path) and (thumbnail_file_path):
       os.remove(flac_path)
       os.remove(thumbnail_file_path)
    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]

    await app.send_message(callback_query.message.chat.id, "You audio already downloaded. Have fun to play!", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("mp3")))
async def downdezmp3(client, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading MP3...")
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])  # Join all parts except the first one
    track_id = track_url.split('/')[-1]  # Extract the track ID from the URL
    track = dez.get_track(track_id)  # Pass the track ID to get_track
    tracks = [track]  # Put the track into a list

    for track in tracks:
            # Schedule download_song to run in the executor
        flac_path = await download_song_mp3_trck(track)
        e = dez.get_track(track.id)
        minutes, seconds = divmod(e.duration, 60)
        duration_formatted = f"{minutes}:{seconds:02}"
        if flac_path is not None:
            song_name = e.title.replace(" ", "_")
            pict = dez.get_track(track.id)
            playlist_thumbnail = pict.album.cover_small
            thumbnail_file_path = resize_image_from_url(playlist_thumbnail, downdir, song_name)
            titles = e.title[:30]
            arttis = e.artist.name[:30]
            reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )
            song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # remove invalid characters
                # thumbnail_file_path = resize_image_from_url(playlist_thumbnail, output_path, thumbnail_name)
            await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
            await app.send_audio(callback_query.message.chat.id, audio=flac_path, title=e.title, performer=e.artist.name, duration=e.duration, thumb=thumbnail_file_path, caption=f"🔗 [Deezer](https://deezer.com/en/track/{track.id})", reply_markup=reply_markup)              

    await message.delete()
    if os.path.exists(flac_path) and (thumbnail_file_path):
       os.remove(flac_path)
       os.remove(thumbnail_file_path)
    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]

    await app.send_message(callback_query.message.chat.id, "You audio already downloaded. Have fun to play!", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("arf")))
async def downdezartistflac(client, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading MP3...")
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])
    artist_id = track_url.split('/')[-1]
    artist = dez.get_artist(artist_id)

    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)

    # Get all albums of the artist
    albums = artist.get_albums()

    artist_tracks = []
    for album in albums:
        tracks = album.get_tracks()
        for track in tracks:
            artist_tracks.append(track)

    if premiumornot == False:
       if len(artist_tracks) > 10:
          await app.send_message(callback_query.message.chat.id, "For now, you can only download 10 tracks. Click /info to upgrade your plan!")
          artist_tracks = artist_tracks[:10]
    else:
       if len(artist_tracks) > 120:
        await app.send_message(callback_query.message.chat.id, "Max Tracks is 120!")
        artist_tracks = artist_tracks[:120]

    tasks = []
    flac_file_paths = []  # Store FLAC paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in artist_tracks:
        try: # Create a dictionary from the track id
            flac_path = await download_song_flac_art(track)  # Download FLAC
            if flac_path is not None:  # Check if download successful
                e = dez.get_track(track.id)  # Use the dictionary instead of the integer
                minutes, seconds = divmod(e.duration, 60)

                song_name = e.title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # Remove invalid characters

                pict = dez.get_track(track.id)  # Use the dictionary instead of the integer
                artist_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(artist_thumbnail, downdir, song_name)
                titles = e.title[:30]
                arttis = artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )

                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                audio_path = str(flac_path)
                if os.path.exists(audio_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track.id})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    flac_file_paths.append(flac_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(flac_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {audio_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track.id}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))
    
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("arm")))
async def downdezartistflac(client, callback_query):
    message = await app.send_message(callback_query.message.chat.id, "Downloading MP3...")
    track_parts = callback_query.data.split(".")
    track_url = ".".join(track_parts[1:])
    artist_id = track_url.split('/')[-1]
    artist = dez.get_artist(artist_id)

    userid = callback_query.from_user.id
    premiumornot = check_user_id(userid)

    # Get all albums of the artist
    albums = artist.get_albums()

    artist_tracks = []
    for album in albums:
        tracks = album.get_tracks()
        for track in tracks:
            artist_tracks.append(track)

    if premiumornot == False:
       if len(artist_tracks) > 60:
          await app.send_message(callback_query.message.chat.id, "For now, you can only download 60 tracks. Click /info to upgrade your plan!")
          artist_tracks = artist_tracks[:60]
    else:
       if len(artist_tracks) > 200:
        await app.send_message(callback_query.message.chat.id, "Max Tracks is 200!")
        artist_tracks = artist_tracks[:200]

    tasks = []
    flac_file_paths = []  # Store FLAC paths for deletion later
    thumbnail_file_paths = []  # Store thumbnail paths for deletion later

    for track in artist_tracks:
        try: # Create a dictionary from the track id
            flac_path = await download_song_mp3_art(track)  # Download FLAC
            if flac_path is not None:  # Check if download successful
                e = dez.get_track(track.id)  # Use the dictionary instead of the integer
                minutes, seconds = divmod(e.duration, 60)

                song_name = e.title.replace(" ", "_")
                song_name = re.sub(r'[\\/*?:"<>|]', "", song_name)  # Remove invalid characters

                pict = dez.get_track(track.id)  # Use the dictionary instead of the integer
                artist_thumbnail = pict.album.cover_small
                thumbnail_file_path = resize_image_from_url(artist_thumbnail, downdir, song_name)
                titles = e.title[:30]
                arttis = artist.name[:30]
                reply_markup = InlineKeyboardMarkup(
                        [
                        [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{arttis}-{titles}")]
                        ]
                        )

                await app.send_chat_action(callback_query.message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                audio_path = str(flac_path)
                if os.path.exists(audio_path):  # Check if the file exists
                    task = asyncio.create_task(
                        app.send_audio(
                            callback_query.message.chat.id, 
                            audio=audio_path, 
                            title=e.title, 
                            performer=e.artist.name, 
                            duration=e.duration, 
                            thumb=thumbnail_file_path, 
                            caption=f"🔗 [Deezer](https://deezer.com/en/track/{track.id})",
                            disable_notification=True,
                            reply_markup=reply_markup
                        )
                    )
                    tasks.append(task)
                    flac_file_paths.append(flac_path)
                    thumbnail_file_paths.append(thumbnail_file_path)
                    await asyncio.gather(*tasks)
                    os.remove(flac_path)
                    os.remove(thumbnail_file_path)
                    await message.delete()
                else:
                    print(f"Audio file not found: {audio_path}")
        except Exception as e:  # Handle download or processing errors
            print(f"Error processing track: {track.id}")
            print(e)

    buttons = [[InlineKeyboardButton("Subscribe", url="https://t.me/nekozux")]]
    # Send a message after all downloads are complete
    await app.send_message(callback_query.message.chat.id, "All audio files have been downloaded. Enjoy your music!", reply_markup=InlineKeyboardMarkup(buttons))

