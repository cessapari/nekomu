import traceback
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from shazamio import Shazam, Serialize
import aiohttp
import aiofiles
from moviepy.editor import VideoFileClip
from tiktok_downloader import snaptik
import os
import yt_dlp
from concurrent.futures import ThreadPoolExecutor
import asyncio
from azapi import AZlyrics
#from instaloader import Instaloader, Post

#L = Instaloader()

# Login or load session
#username = 'nekozux'
#password = 'farih2009'
#L.login(username, password)

api_id = '2374504'
api_hash = '2ea965cd0674f1663ec291313edcd333'
bot_token = '6836150963:AAFIZQcYf6_ak2smcnMoJna2xiBkw1UldhU'

app = Client("nekomusselasarabu", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("start"))
async def startmessage(client, msg):
    await msg.reply_text("Hello! I'm a bot that can recognize songs. Just send me an audio file or a link to a social media post and I'll tell you the song name and artist.")

@app.on_message(filters.audio | filters.voice | filters.video)
async def audio_handler(client, message):
    try:
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
        await message.reply_text(f"Cannot extract your Media. report error at @farihdzaky")
        traceback.print_exc()  # This will print the traceback
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists(f'{username}_album_art.jpg'):
            os.remove(f'{username}_album_art.jpg')

@app.on_message(filters.text)
async def link_handler(client, message):
    audio_file = None
    video_file = None
    try:
        userid = message.from_user.id
        username = message.from_user.username
        link = message.text

        # Only process messages with links from TikTok, Instagram, Facebook, YouTube Shorts, and Twitter
        if 'tiktok.com' in link:
            d = snaptik(link)
            video_file = f'{userid}.mp4'
            d[0].download(video_file)
            
            # Extract audio from the downloaded video
            video = VideoFileClip(video_file)
            video.audio.write_audiofile(f"{userid}.mp3")
            audio_file = f'{userid}.mp3'
            # Process the extracted audio
            await process_audio_file(audio_file, message, username)
        #elif 'instagram.com' in link:
            #post = Post.from_shortcode(L.context, link.split("/")[-2])
            #target = f"{post.owner_username}"
            #L.download_post(post, target=target)
            #filename = f"{post.date_local.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.mp4"
            #filepath = os.path.join(os.getcwd(), target, filename)
            #fileVid = VideoFileClip()
        elif any(substring in link for substring in ['facebook.com', 'youtube.com/shorts', 'x.com']):
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
                future = executor.submit(yt_dlp.YoutubeDL(ydl_opts).download, [link])
                future.result()
            audio_file = f'{userid}.mp3'

            # Process the downloaded audio
            await process_audio_file(audio_file, message, username)

    except Exception as e:
        await message.reply_text(f"Cannot extract your Link. Report error at @farihdzaky")
        traceback.print_exc()  # Print traceback for debugging

    finally:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(f'{username}_album_art.jpg'):
            os.remove(f'{username}_album_art.jpg')

async def get_lyrics(title):
    loop = asyncio.get_event_loop()
    api = AZlyrics("google")
    api.title = title

    # Run the blocking getLyrics function in a separate thread
    lyrics = await loop.run_in_executor(None, api.getLyrics)
    return lyrics

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("lyrics")))
async def searchlyrics(_, callback_query):
    teks = callback_query.data.split(".")
    splitteks = ".".join(teks[1:])
    lyrik = await get_lyrics(splitteks)
    await app.send_message(callback_query.message.chat.id, f"{splitteks}\n\n{lyrik}\n\n**@nekomubot**")
            
async def process_audio_file(audio_file, message, username):
    shazam = Shazam()
    out = await shazam.recognize(audio_file)
    if out:
        title = out['track']['title'] if 'title' in out['track'] else "Unknown"
        artist = out['track']['subtitle'] if 'subtitle' in out['track'] else "Unknown"
        album_art = out['track']['images']['coverarthq'] if 'images' in out['track'] and 'coverarthq' in out['track']['images'] else "Unknown"
        song_url = out['track']['url'] if 'url' in out['track'] else "Unknown"
        release_date = out['track']['release_date'] if 'release_date' in out['track'] else "Unknown"
        album = out['track']['sections'][0]['metadata'][0]['text'] if 'sections' in out['track'] and 'metadata' in out['track']['sections'][0] and out['track']['sections'][0]['metadata'][0]['text'] else "Unknown"
        genre = out['track']['genres']['primary'] if 'genres' in out['track'] and 'primary' in out['track']['genres'] else "Unknown"
        getyturl = Serialize.full_track(data=out)
        youtube_data = await shazam.get_youtube_data(link=getyturl.track.youtube_link)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(album_art) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f'{username}_album_art.jpg', mode='wb') as f:
                        await f.write(await resp.read())

        if youtube_data and album_art is not None:
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
            
            with ThreadPoolExecutor() as executor:  # Use ThreadPoolExecutor directly
                future = executor.submit(yt_dlp.YoutubeDL(ydl_opts).download, [video_link.uri])
                future.result()
                
            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Youtube", url=video_link.uri)],
                    [InlineKeyboardButton("Spotify", url=f"https://open.spotify.com/search/{title}")],
                    [InlineKeyboardButton("Deezer", url=f"https://www.deezer.com/search/{title}")]
                ]
            )
            keyboardlyrics = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{title}")]
                ]
            )
            await message.reply_photo(photo=open(f'{username}_album_art.jpg', 'rb'), caption=caption, reply_markup=keyboard)
            await message.reply_audio(audio=open(f'{username}_video.mp3', 'rb'), reply_markup=keyboardlyrics)
        elif youtube_data is None:
            caption = f"Here's the song you were looking for, @{username}!\n\nSong: {title}\nArtist: {artist}\nGenre: {genre}\nAlbum: {album}\nRelease Date: {release_date}"
            keyboards = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Youtube", url=f"https://youtube.com/search?q={title}")],
                    [InlineKeyboardButton("Spotify", url=f"https://open.spotify.com/search/{title}")],
                    [InlineKeyboardButton("Deezer", url=f"https://www.deezer.com/search/{title}")]
                ]
            )
            await message.reply_photo(photo=open(f'{username}_album_art.jpg', 'rb'), caption=caption, reply_markup=keyboards)
        elif album_art and youtube_data is None:
            caption = f"Here's the song you were looking for, @{username}!\n\nSong: {title}\nArtist: {artist}\nGenre: {genre}\nAlbum: {album}\nRelease Date: {release_date}"
            keyboards = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Youtube", url=f"https://youtube.com/search?q={title}")],
                    [InlineKeyboardButton("Spotify", url=f"https://open.spotify.com/search/{title}")],
                    [InlineKeyboardButton("Deezer", url=f"https://www.deezer.com/search/{title}")]
                ]
            )
            await message.reply_text(caption)
        elif album_art is None:
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
            
            with ThreadPoolExecutor() as executor:  # Use ThreadPoolExecutor directly
                future = executor.submit(yt_dlp.YoutubeDL(ydl_opts).download, [video_link.uri])
                future.result()
                
            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Youtube", url=video_link.uri)],
                    [InlineKeyboardButton("Spotify", url=f"https://open.spotify.com/search/{title}")],
                    [InlineKeyboardButton("Deezer", url=f"https://www.deezer.com/search/{title}")]
                ]
            )
            keyboardlyrics = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Lyrics", callback_data=f"lyrics.{title}")]
                ]
            )
            await message.reply_text(caption, reply_markup=keyboard)
            await message.reply_audio(audio=open(f'{username}_video.mp3', 'rb'), reply_markup=keyboardlyrics)
    else:
        await message.reply_text("Sorry, I couldn't recognize the song.")
        
print('started')
app.run()
