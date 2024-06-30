from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot import app, check_user_id
from pyrogram import enums
from pyrogram import filters
import traceback
from urllib.parse import urlparse
import traceback
import yt_dlp
from shazamio import Shazam, Serialize
import aiohttp
import aiofiles
from moviepy.editor import VideoFileClip
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os

@app.on_message(filters.audio | filters.voice | filters.video)
async def audio_handler(client, message):
    try:
        meshe = await app.send_message(message.chat.id, 'Recognizing')
        userid = message.from_user.id
        username = message.from_user.username
        if message.video:
            video_file = await message.download(f"{userid}.mp4")
            clip = VideoFileClip(video_file)
            clip.audio.write_audiofile(f"{userid}.mp3")
            audio_file = f"{userid}.mp3"
        else:
            audio_file = await message.download(f"{userid}.mp3") if message.audio else await message.download(f"{userid}.ogg")

        await process_audio_file(audio_file, message, username)
    except Exception as e:
        await message.reply_text(f"Cannot extract your Media. Report error at @farihdzaky")
        traceback.print_exc()  # This will print the traceback
    finally:
        await meshe.delete()  # Delete the "Recognizing" message
        if os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists(f'{username}_album_art.jpg'):
            os.remove(f'{username}_album_art.jpg')

@app.on_callback_query(filters.create(lambda _, __, query: query.data == "delete"))
async def delete_message(_, callback_query):
    await app.delete_messages(chat_id=callback_query.message.chat.id, message_ids=callback_query.message.id)

async def process_audio_file(audio_file, message, username):
    shazam = Shazam()
    out = await shazam.recognize(audio_file)
    userid = message.from_user.id
    premuser = check_user_id(str(userid))
    
    if out:
        title = out.get('track', {}).get('title', "Unknown")
        artist = out.get('track', {}).get('subtitle', "Unknown")
        album_art = out.get('track', {}).get('images', {}).get('coverarthq', "Unknown")
        song_url = out.get('track', {}).get('url', "Unknown")
        release_date = out.get('track', {}).get('release_date', "Unknown")
        album = out.get('track', {}).get('sections', [{}])[0].get('metadata', [{}])[0].get('text', "Unknown")
        genre = out.get('track', {}).get('genres', {}).get('primary', "Unknown")
        
        artist = artist[:30]
        title = title[:30]
        
        getyturl = Serialize.full_track(data=out)
        
        async with aiohttp.ClientSession() as session:
            if album_art and urlparse(album_art).scheme:
                async with session.get(album_art) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(f'{username}_album_art.jpg', mode='wb') as f:
                            await f.write(await resp.read())
                    else:
                        print('cannot find any thumbnail')
        
        if getyturl and getyturl.track and getyturl.track.youtube_link:
            youtube_links = getyturl.track.youtube_link
            if isinstance(youtube_links, str):
                youtube_links = [youtube_links]
            for link in youtube_links:
                youtube_data = await shazam.get_youtube_data(link=link)
                if youtube_data:
                    video_link = Serialize.youtube(data=youtube_data)
                    caption = f"Here's the song you were looking for, @{username}!\n\nSong: {title}\nArtist: {artist}\nGenre: {genre}\nAlbum: {album}\nRelease Date: {release_date}"
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': f'{username}_video.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '320',
                        }],
                    }
                    ydl_ops2 = {
                        'format': 'bestaudio/best',
                        'outtmpl': f'{username}_audio.%(ext)s',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'flac',
                        }]
                    }
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(yt_dlp.YoutubeDL(ydl_ops2 if premuser else ydl_opts).extract_info, video_link.uri)
                        info = future.result()
                    duration = info.get('duration', "Unknown")
                    keyboard = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Youtube", url=video_link.uri)],
                            [InlineKeyboardButton("Shazam", url=song_url)]
                        ]
                    )
                    keyboardlyrics = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{artist}-{title}")]
                        ]
                    )
                    executor.shutdown(wait=True)
                    audio_file_path = f'{username}_audio.flac' if premuser else f'{username}_video.mp3'
                    await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
                    if os.path.exists(f'{username}_album_art.jpg'):
                        await message.reply_photo(photo=open(f'{username}_album_art.jpg', 'rb'), caption=caption, reply_markup=keyboard)
                        if os.path.exists(audio_file_path):
                            await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                            await message.reply_audio(audio=open(audio_file_path, 'rb'), title=title, performer=artist, duration=duration, reply_markup=keyboardlyrics)
                            os.remove(audio_file_path)
                        else:
                            await app.send_message(message.chat.id, "Sorry, I couldn't find the audio file.", reply_to_message_id=message.id)
                    else:
                        await message.reply_text(caption, reply_markup=keyboard)
                        if os.path.exists(audio_file_path):
                            await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_AUDIO)
                            await message.reply_audio(audio=open(audio_file_path, 'rb'), title=title, performer=artist, duration=duration, reply_markup=keyboardlyrics)
                            os.remove(audio_file_path)
                        else:
                            await app.send_message(message.chat.id, "Sorry, I couldn't find the audio file.", reply_to_message_id=message.id)
                    os.remove(f'{username}_album_art.jpg')
                else:
                    caption = f"Here's the song you were looking for, @{username}!\n\nSong: {title}\nArtist: {artist}\nGenre: {genre}\nAlbum: {album}\nRelease Date: {release_date}"
                    keyboards = InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Youtube", url=f"https://youtube.com/search?q={title}")],
                            [InlineKeyboardButton("Shazam", url=song_url)]
                        ]
                    )
                    if os.path.exists(f'{username}_album_art.jpg'):
                        await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
                        await message.reply_photo(photo=open(f'{username}_album_art.jpg', 'rb'), caption=caption, reply_markup=keyboards)
                        os.remove(f'{username}_album_art.jpg')
                    else:
                        await app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                        await message.reply_text(caption, reply_markup=keyboards)
        else:
            caption = f"Here's the song you were looking for, @{username}!\n\nSong: {title}\nArtist: {artist}\nGenre: {genre}\nAlbum: {album}\nRelease Date: {release_date}"
            keyboards = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Shazam", url=song_url)]
                ]
            )
            if os.path.exists(f'{username}_album_art.jpg'):
                await app.send_chat_action(message.chat.id, enums.ChatAction.UPLOAD_PHOTO)
                await message.reply_photo(photo=open(f'{username}_album_art.jpg', 'rb'), caption=caption)
                os.remove(f'{username}_album_art.jpg')
            else:
                await app.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
                await message.reply_text(caption)
    else:
        await app.send_message(message.chat.id, "Sorry i couldn't find any results for that song!", reply_to_message_id=message.id)
