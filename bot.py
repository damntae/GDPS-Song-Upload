import disnake
from disnake.ext import commands
import requests
import random
import mysql.connector
from ftplib import FTP
import os

config = {
    'host': '', # хост: serverXXX.hosting.reg.ru / sql.5v.pl и т.д.
    'user': '', # юзернейм бд
    'password': '', # пароль от базы данных
    'database': '', # название базы данных
    'port': 3306,
}

fgdps_logo = '''
  █████▒ ▄████ ▓█████▄  ██▓███    ██████     █    ██ ▄▄▄█████▓ ██▓ ██▓     ██▓▄▄▄█████▓ ██▓▓█████   ██████ 
▓██   ▒ ██▒ ▀█▒▒██▀ ██▌▓██░  ██▒▒██    ▒     ██  ▓██▒▓  ██▒ ▓▒▓██▒▓██▒    ▓██▒▓  ██▒ ▓▒▓██▒▓█   ▀ ▒██    ▒ 
▒████ ░▒██░▄▄▄░░██   █▌▓██░ ██▓▒░ ▓██▄      ▓██  ▒██░▒ ▓██░ ▒░▒██▒▒██░    ▒██▒▒ ▓██░ ▒░▒██▒▒███   ░ ▓██▄   
░▓█▒  ░░▓█  ██▓░▓█▄   ▌▒██▄█▓▒ ▒  ▒   ██▒   ▓▓█  ░██░░ ▓██▓ ░ ░██░▒██░    ░██░░ ▓██▓ ░ ░██░▒▓█  ▄   ▒   ██▒
░▒█░   ░▒▓███▀▒░▒████▓ ▒██▒ ░  ░▒██████▒▒   ▒▒█████▓   ▒██▒ ░ ░██░░██████▒░██░  ▒██▒ ░ ░██░▒████▒▒██████▒▒
 ▒ ░    ░▒   ▒  ▒▒▓  ▒ ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░   ░▒▓▒ ▒ ▒   ▒ ░░   ░▓  ░ ▒░▓  ░░▓    ▒ ░░   ░▓  ░░ ▒░ ░▒ ▒▓▒ ▒ ░
 ░       ░   ░  ░ ▒  ▒ ░▒ ░     ░ ░▒  ░ ░   ░░▒░ ░ ░     ░     ▒ ░░ ░ ▒  ░ ▒ ░    ░     ▒ ░ ░ ░  ░░ ░▒  ░ ░
 ░ ░   ░ ░   ░  ░ ░  ░ ░░       ░  ░  ░      ░░░ ░ ░   ░       ▒ ░  ░ ░    ▒ ░  ░       ▒ ░   ░   ░  ░  ░  
             ░    ░                   ░        ░               ░      ░  ░ ░            ░     ░  ░      ░  
                ░                                                                                                                
'''

print(fgdps_logo)
print()
print("Loading...")

bot = commands.Bot()
conn = mysql.connector.connect(**config)
cursor = conn.cursor()
token = "" # токен бота

@bot.event
async def on_ready():
    print('[bot] Bot started')

@bot.slash_command(description="Загрузка музыки с помощью слэш-команды")
async def upload_music(ctx, songname: str, file: disnake.Attachment, authorname: str = 'FGDPS Song Reupload'):
    await ctx.send('Загружаем песню на сервер, подождите...')
    # 1 - Reupload
    if authorname != 'FGDPS Song Reupload':
        authorID = random.randint(1111111, 8000000)
    else:
        authorID = 1
    musicID = random.randint(1111111, 8000000)

    if not file.filename.endswith('.mp3'):
        return await ctx.send('Данное расширение файла не поддерживается, только `.mp3`.')

    file_path = f"/www/адрес.сервера/server/song/data/{musicID}.mp3" # адрес сервера, к примеру: faneriagdps.xyz

    # Создание директории, если она не существует
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    await file.save(file_path)

    file_size = os.path.getsize(file_path) / (1024 * 1024)
    hash = ''

    url = f"https://адрес.сервера/server/song/data/{musicID}.mp3" # адрес сервера, к примеру: faneriagdps.xyz

    cursor.execute(f'INSERT INTO songs (ID, name, authorID, authorName, size, download, hash) VALUES ({musicID}, "{songname}", {authorID}, "{authorname}", {file_size}, "{url}", "{hash}")')
    conn.commit()

    ftp_host = '' # фтп хост, к примеру: fnafafa.5v.pl / serverXXX.hosting.reg.ru
    ftp_user = '' # фтп юзер
    ftp_password = '' # пароль от фтп
    ftp_directory = '/www/адрес.сервера/server/song/data/' # адрес сервера, к примеру: faneriagdps.xyz

    with FTP(ftp_host) as ftp:
        ftp.login(ftp_user, ftp_password)
        ftp.cwd(ftp_directory)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {musicID}.mp3', file)

    os.chmod(file_path, 0o755)

    php_script_url = 'https://адрес.сервера/server/song/stuff.php' # адрес сервера, к примеру: faneriagdps.xyz
    data = {'title': songname}

    response = requests.post(php_script_url, data=data)

    if response.ok:
        await ctx.send(f'Песня загружена! | ID: {musicID}')
    else:
        await ctx.send('блядская ошибка опять')

bot.run(token)
