# Lyrics module
import requests
from bs4 import BeautifulSoup
from pyrogram import filters
from bot import app
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import os

# Genius Token
GENIUS_API_TOKEN = 'hWLVRC0kGyj02lLPobHfLE-fZhcHiwfzrVy0DTF1wbLppwHPqKW5UNHMSKazwfEM'

# Function to search for a song on Genius
def infogenius(query):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
    search_url = f'{base_url}/search'
    params = {'q': query}

    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        hits = data['response']['hits']
        if hits:
            song_data = hits[0]['result']
            song_info = {
                'title': song_data['title'],
                'artist': song_data['primary_artist']['name'],
                'thumbnail': song_data['song_art_image_thumbnail_url'],
                'date': song_data['release_date_for_display'],
                'url': song_data['url']
            }
            return song_info
        else:
            print('No results found.')
            return None
    else:
        print(f'Error: {response.status_code}')
        return None

# Fungsi untuk mendapatkan informasi lagu berdasarkan nama lagu
async def get_song_info(name):
    song_info = infogenius(name)
    return song_info

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("lyrics")))
async def getinformationlyrics(_, callback_query):
    try:
        message = await app.send_message(callback_query.message.chat.id, "Wait for a while...")
        teks = callback_query.data.split(".")
        artist, title = ".".join(teks[1:]).split("-")  # Misalkan format data adalah "lyrics:judul_lagu"
        song_info = await get_song_info(f"{artist} {title}")
        if not song_info:
            song_info = await get_song_info(f"{title}")
        if song_info:
            info_message = f"Title: {song_info['title']}\n" \
                           f"Artist: {song_info['artist']}\n" \
                           f"Release Date: {song_info['date']}\n"
            inlinekey = InlineKeyboardMarkup([
                [InlineKeyboardButton("Genius", url=song_info['url']),
                 InlineKeyboardButton("As Msg", callback_data=f"lymsg.{artist}-{title}"),
                 InlineKeyboardButton("As LRC", callback_data=f"download_lrc.{artist}-{title}"),
                 InlineKeyboardButton("As TXT", callback_data=f"download_txt.{artist}-{title}")],
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.send_photo(chat_id=callback_query.message.chat.id, photo=song_info['thumbnail'], caption=info_message, reply_markup=inlinekey)
        else:
            await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message.message_id, text="No information from the song.")
    except Exception as e:
        await app.send_message(callback_query.message.chat.id, f"Error: {str(e)}")
        
def search_genius(query):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
    search_url = f'{base_url}/search'
    params = {'q': query}
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def scrape_lyrics(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        lyrics_div = soup.find('div', class_='lyrics')
        if not lyrics_div:
            lyrics_div = soup.find_all('div', {'data-lyrics-container': 'true'})
        if lyrics_div:
            lyrics = "\n".join([div.get_text(separator='\n').strip() for div in lyrics_div])
            return lyrics
        else:
            print('Could not find the lyrics on the page.')
            return None
    else:
        print(f'Failed to retrieve the page. Status code: {response.status_code}')
        return None

async def get_lyrics(name):
    song_info = search_genius(name)
    if song_info:
        song = song_info['response']['hits'][0]['result']
        song_url = song['url']
        lyrics = scrape_lyrics(song_url)
        return lyrics
    return None

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("lymsg")))
async def searchlyrics(_, callback_query):
    try:
        message = await app.send_message(callback_query.message.chat.id, "Wait for a while...")
        teks = callback_query.data.split(".")
        artist, title = ".".join(teks[1:]).split("-")

        # Get the lyrics using the get_lyrics function
        lyrics = await get_lyrics(f"{artist} {title}")

        if not lyrics:
            # If lyrics are not found, try getting lyrics with just the title
            lyrics = await get_lyrics(title)

        if not lyrics:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message.id, text=f"Not found any lyrics from artist {artist} title {title}!", reply_markup=reply_markup)
        else:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            
            # Split lyrics into chunks of 4000 characters (leaving some space for headers)
            chunks = [lyrics[i:i+4000] for i in range(0, len(lyrics), 4000)]
            
            for i, chunk in enumerate(chunks):
                if i == 0:
                    header = f"{artist} - {title}\n\n"
                else:
                    header = f"{artist} - {title} (cont)\n\n"
                
                footer = "\n\n**@nekomubot**"
                message_text = f"{header}{chunk}{footer}"
                
                if i == 0:
                    await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message.id, text=message_text, reply_markup=reply_markup)
                else:
                    await app.send_message(chat_id=callback_query.message.chat.id, text=message_text, reply_markup=reply_markup)

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print traceback
        await app.send_message(callback_query.message.chat.id, 'Error: Cannot fetch the lyrics')
        
def create_lrc_file(artist, title, lyrics):
    # Create a filename-safe version of the artist and title
    filename = re.sub(r'[^\w\-_\. ]', '_', f"{artist} - {title}").strip()
    filename = f"{filename}.lrc"
    
    # Prepare LRC content
    lrc_content = f"[ar:{artist}]\n[ti:{title}]\n\n"
    for line in lyrics.split('\n'):
        if line.strip():  # Skip empty lines
            lrc_content += f"[00:00.00]{line}\n"
    
    # Save to file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(lrc_content)
    
    return filename

@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("download_lrc")))
async def searchlyrics(_, callback_query):
    try:
        message = await app.send_message(callback_query.message.chat.id, "Wait for a while...")
        teks = callback_query.data.split(".")
        artist, title = ".".join(teks[1:]).split("-")

        # Get the lyrics using the get_lyrics function
        lyrics = await get_lyrics(f"{artist} {title}")

        if not lyrics:
            # If lyrics are not found, try getting lyrics with just the title
            lyrics = await get_lyrics(title)

        if not lyrics:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message.id, text=f"Not found any lyrics from artist {artist} title {title}!", reply_markup=reply_markup)
        else:
            # Create LRC file
            lrc_filename = create_lrc_file(artist, title, lyrics)
            
            # Send the LRC file
            await app.send_document(
                chat_id=callback_query.message.chat.id,
                document=lrc_filename,
                caption=f"LRC file for {artist} - {title}\n\n**@nekomubot**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Channel', url=f'https://t.me/nekozuX')]])
            )
            
            # Delete the temporary file
            os.remove(lrc_filename)
            
            # Edit the original message
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=message.id,
                text=f"LRC file for {artist} - {title} has been sent.",
                reply_markup=reply_markup
            )

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print traceback
        await app.send_message(callback_query.message.chat.id, 'Error: Cannot fetch the lyrics')
        
@app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("download_txt")))
async def searchlyrics(_, callback_query):
    try:
        message = await app.send_message(callback_query.message.chat.id, "Wait a sec...")
        teks = callback_query.data.split(".")
        artist, title = ".".join(teks[1:]).split("-")

        # Dapatkan lirik menggunakan fungsi get_lyrics
        lyrics = await get_lyrics(f"{artist} {title}")

        if not lyrics:
            # Jika lirik tidak ditemukan, coba cari dengan judul saja
            lyrics = await get_lyrics(title)

        if not lyrics:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.edit_message_text(chat_id=callback_query.message.chat.id, message_id=message.id, text=f"Not found any lyrics {artist} - {title}!", reply_markup=reply_markup)
        else:
            # Buat file TXT
            txt_filename = create_txt_file(artist, title, lyrics)
            
            # Kirim file TXT
            await app.send_document(
                chat_id=callback_query.message.chat.id,
                document=txt_filename,
                caption=f"File TXT for {artist} - {title}\n\n**@nekomubot**",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Channel', url=f'https://t.me/nekozuX')]])
            )
            
            # Hapus file sementara
            os.remove(txt_filename)
            
            # Edit pesan asli
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌", callback_data="delete")]
            ])
            await app.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=message.id,
                text=f"File TXT for {artist} - {title} has been sent.",
                reply_markup=reply_markup
            )

    except Exception as e:
        import traceback
        traceback.print_exc()  # Cetak traceback
        await app.send_message(callback_query.message.chat.id, 'Error: Cannot fetch lyrics')

def create_txt_file(artist, title, lyrics):
    # Buat nama file yang aman
    filename = re.sub(r'[^\w\-_\. ]', '_', f"{artist} - {title}").strip()
    filename = f"{filename}.txt"
    
    # Siapkan konten TXT
    txt_content = f"{artist} - {title}\n\n{lyrics}"
    
    # Simpan ke file
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(txt_content)
    
    return filename





