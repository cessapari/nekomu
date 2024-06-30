import os
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import time
import requests
from PIL import Image
from pydub import AudioSegment
from io import BytesIO
import asyncio

async def progress(current, total, message: Message, start, progress_type, song_name):
    try:
        elapsed_time = time.time() - start
        completed = round((current / total) * 100)
        text = f"**Don't forget to subscribe @nekozux :D**\n" \
               f"**{progress_type} {song_name}**\nProgress: {completed}%\n" \
               f"Elapsed time: {int(elapsed_time)}s\n" \
               f"File size: {total / 1024 / 1024:.2f} MB"
        await message.edit_text(text)

        # Introduce a small pause between edits for proactive rate limiting
        await asyncio.sleep(1)
    except FloodWait as e:
        # Exponential backoff for repeated flood wait errors
        sleep_duration = min(e.seconds * 2, 60)  # Limit max sleep to 60 seconds
        print(f"Flood wait encountered. Sleeping for {sleep_duration} seconds.")
        await asyncio.sleep(sleep_duration)
    except Exception as ex:
        print(f"An error occurred during progress update: {ex}")

def bytes_to_kilobytes(bytes):
    return bytes / 1024.0

def convert_mp3_to_flac(mp3_path):
    audio = AudioSegment.from_file(mp3_path, format="mp3")
    flac_io = BytesIO()
    audio.export(flac_io, format="flac")
    flac_bytes = flac_io.getvalue()
    return flac_bytes

def resize_image_from_url(url, output_path, name):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        print(f"Image size: {len(response.content)} bytes width: {img.width} height: {img.height}")
        
        # Resize the image with a high-quality downsampling algorithm
        resized_img = img.resize((90, 90), resample=Image.LANCZOS)
        print(f"Resized image size: {resized_img.size} bytes width: {resized_img.width} height: {resized_img.height}")
        
        # Include the name in the output file path
        output_file_path = os.path.join(output_path, f"{name}.jpeg")
        
        resized_img.save(output_file_path, "JPEG", optimize=True)
        return output_file_path

    except Exception as e:
        print(f"Error processing image: {e}")
        return None
    
def convert_ogg_to_mp3(input_file, output_file):
    audio = AudioSegment.from_ogg(input_file)
    audio.export(output_file, format="mp3", bitrate="320k")
    return output_file

def convert_ogg_to_high_quality_flac(ogg_path, high_quality_flac_path):
    # Check if the input file exists
    if not os.path.exists(ogg_path):
        print(f"Input file does not exist: {ogg_path}")
        return None

    # Check if the output directory exists
    output_dir = os.path.dirname(high_quality_flac_path)
    if not os.path.exists(output_dir):
        print(f"Output directory does not exist: {output_dir}")
        return None

    # Try to convert the file
    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(high_quality_flac_path, format="flac", codec="flac", bitrate="1000k")
    except Exception as e:
        print(f"Failed to convert file: {e}")
        return None

    return high_quality_flac_path

def convert_ogg_to_500kbps(ogg_path, output_path):
        # Check if the input file exists
        if not os.path.exists(ogg_path):
            print(f"Input file does not exist: {ogg_path}")
            return None

        # Check if the output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            print(f"Output directory does not exist: {output_dir}")
            return None

        # Try to convert the file
        try:
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(output_path, format="ogg", bitrate="500k")
        except Exception as e:
            print(f"Failed to convert file: {e}")
            return None

        return output_path