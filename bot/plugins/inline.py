from bot import app
from bot.plugins.lyrics import get_lyrics, get_song_info
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
import uuid

@app.on_inline_query()
async def inline_query_handler(client, query):
    try:
        if len(query.query) < 3:
            return

        lyrics = await get_lyrics(query.query)
        if not lyrics:
            return

        song_info = await get_song_info(query.query)
        if not song_info:
            return

        title = song_info['title']
        artist = song_info['artist']
        
        # Batasi lirik menjadi 3800 karakter untuk inline query
        if len(lyrics) > 3800:
            truncated_lyrics = lyrics[:3800]
            continuation_link = f"https://t.me/nekomubot?start=lyrics_{artist.replace(' ', '_')}_{title.replace(' ', '_')}"
            truncated_lyrics += f"\n\n... [Continue]({continuation_link})"
        else:
            truncated_lyrics = lyrics

        message_text = f"**{artist} - {title}**\n\n{truncated_lyrics}"
        
        result = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"Lirik: {artist} - {title}",
                input_message_content=InputTextMessageContent(message_text, disable_web_page_preview=True),
                description=truncated_lyrics[:100] + "...",
                thumb_url=song_info['thumbnail'],
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("See at genius!", url=song_info['url'])]])
            )
        ]

        await query.answer(result, cache_time=300)
    except Exception as e:
        print(f"Error in inline query: {str(e)}")
