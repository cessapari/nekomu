import requests
import asyncio

# Token API Genius Anda
GENIUS_API_TOKEN = 'hWLVRC0kGyj02lLPobHfLE-fZhcHiwfzrVy0DTF1wbLppwHPqKW5UNHMSKazwfEM'

# Fungsi untuk mencari lagu di Genius dan mengambil semua informasi langsung dari API
def search_genius(query):
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
            return song_data
        else:
            print('No results found.')
            return None
    else:
        print(f'Error: {response.status_code}')
        return None

# Fungsi untuk mendapatkan informasi lagu berdasarkan nama lagu
async def get_song_info(name):
    song_info = search_genius(name)
    return song_info

# Contoh penggunaan fungsi
async def main():
    song_name = 'Cigarattes after sex - Sunsetz'
    info = await get_song_info(song_name)
    if info:
        print(f'Informasi untuk {song_name}:')
        print(info)
    else:
        print(f'Tidak dapat menemukan informasi untuk {song_name}.')

if __name__ == '__main__':
    asyncio.run(main())
