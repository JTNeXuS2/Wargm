#requests
# py -3 -m pip install -U disnake
# pip install requests
import disnake
from disnake.ext import commands
from disnake import Intents
import requests
import json
import asyncio
import configparser
import re
import unicodedata
from datetime import datetime, timedelta

##################################################
##				CONFIG FUNCTIONS				##
def read_cfg():
    config = configparser.ConfigParser(interpolation=None)
    try:
        with open('config.ini', 'r', encoding='utf-8') as file:
            config.read_file(file)
    except FileNotFoundError:
        print("Error: Config.ini not found.")
        return None
    return config

async def write_cfg(section, key, value):
    config = read_cfg()
    if f'{section}' not in config:
        config[f'{section}'] = {}
    config[f'{section}'][f'{key}'] = str(f'{value}')

    with open('config.ini', 'w', encoding='utf-8') as configfile:
        config.write(configfile)

async def del_cfg(section, key):
    config = read_cfg()
    try:
        if 'server' in config and key in config['server']:
            config.remove_option('server', key)
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            print(f"Ключ {key} удален из блока [server] в конфигурационном файле.")
        else:
            print(f"Ключ {key} не найден в блоке [server] или блок [server] отсутствует.")
    except Exception as e:
        print(f"Произошла ошибка при удалении {key}: {e}")

def update_settings():
    global bot_token, shopid, shop_token, bonusdays, timer, channel_id, wargm_url, lists

    config = read_cfg()

    if config:
        try:
            bot_token = config['botconfig']['bot_token']
            shopid = config['botconfig']['shopid']
            shop_token = config['botconfig']['shop_token']
            bonusdays = config['botconfig']['bonusdays']
            timer = config['botconfig']['timer']
            wargm_url = config['botconfig']['wargm_url']
            channel_id = config['botconfig']['channel_id']
            lists = {key: value for key, value in config['server'].items()}

        except KeyError as e:
            print(f"Error: wrong lines in config file {e}")

update_settings()

##################################################
##				BOT FUNCTIONS					##

async def check_operations():
    #request
    url = f'{wargm_url}/operations?client={shopid}:{shop_token}&status=pending'
    json_data = ''
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print("Ошибка при выполнении запроса. Код ошибки:", response.status_code)
    return

async def close_traide():
    return
async def get_traid(operations):
    #current_date = datetime.now()
    future_date = datetime.now() + timedelta(days=int(bonusdays))
    formatted_date = future_date.strftime("%Y-%m-%d")

    for key, value in operations['responce']['data'].items():
        if f"{value.get('claimed')}" == "1":
            print(f'claimed!')
            break

        print("--- Operation ---")
        print("id:", value.get('id'))
        print("player:", value.get('player'))
        print("user_id:", value.get('user_id'))
        print("user_steam_id:", value.get('user_steam_id'))
        print("server_id:", value.get('server_id'))
        print("offer_id:", value.get('offer_id'))
        print("item:", value.get('item'))
        print("amount:", value.get('amount'))
        print("set_count:", value.get('set_count'))
        print("buy_count:", value.get('buy_count'))
        print("status:", value.get('status'))
        print("claimed:", value.get('claimed'))
        
        id = value.get('id')
        player = value.get('player')
        user_id = value.get('user_id')
        user_steam_id = value.get('user_steam_id')
        server_id = value.get('server_id')
        offer_id = value.get('offer_id')
        item = value.get('item')
        amount = value.get('amount')
        set_count = value.get('set_count')
        buy_count = value.get('buy_count')
        status = value.get('status')
        claimed = value.get('claimed')

        #начислить
        if str(offer_id) in lists:
            print(f"offer_id {offer_id} найден в словаре lists.")
            value = lists[str(offer_id)]
            target_server_id = value.split(':')[0].strip()
            print(f'начисляем на сервере {target_server_id}')
            channel = await bot.fetch_channel(channel_id)
            try:
                #Операция начисления
                url = f'{wargm_url}/add_bonus?client={shopid}:{shop_token}&user_id={user_id}&server_id={target_server_id}&amount={buy_count}&expire={formatted_date}'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    #Операция c ошибкой?
                    if data.get("responce", {}).get("status") == "error":
                        msg = data["responce"].get("msg", "Нет сообщения")
                        print(f"-> Ошибка wargm API: {msg}")
                        print("Содержимое ответа:", json.dumps(data, indent=4))
                        url = f'{wargm_url}/operation_cancel?client={shopid}:{shop_token}&operation_id={id}'
                        response = requests.get(url)
                        if response.status_code == 200:
                            await channel.send(f'Ошибка операции **{id}**\n'
                                               f'Описание: **{msg}**\n'
                                               f'**Бонусы возвращены: {buy_count}**\n'
                                               f'Ник: **{player}**\n'
                                               f'Аккаунт: **{user_id}**\n'
                                               f'Steam ID: **{user_steam_id}**\n'
                                               f'Сервер списания wargm.ru/server/{server_id}/votes\n'
                                               f'Сервер начисления wargm.ru/server/{target_server_id}/votes\n'
                                               f'Ответ WG API:" {json.dumps(data, indent=4)} @here'
                                               )
                            print("Позиция отменена\n")
                        break
                    print(f"Бонусы начислены и действительны {bonusdays} дней: {formatted_date}")

                    #Закрываем операцию
                    url = f'{wargm_url}/operation_success?client={shopid}:{shop_token}&operation_id={id}'
                    response = requests.get(url)
                    if response.status_code == 200:
                        await channel.send(f'Выполнена операция **{id}**\n'
                                           f'Бонусы зачислены: **{buy_count}**\n'
                                           f'Ник: **{player}**\n'
                                           f'Аккаунт: **{user_id}**\n'
                                           f'Steam ID: **{user_steam_id}**\n'
                                           f'Сервер списания wargm.ru/server/{server_id}/votes\n'
                                           f'Сервер начисления wargm.ru/server/{target_server_id}/votes\n'
                                           )
                        print("Позиция закрыта\n")
            except Exception as e:
                print("Ошибка при начислении. Код ошибки:", response.status_code)

##################################################
##					BOT BODY					##
prefix = '/'
intents = disnake.Intents.default()
intents = disnake.Intents().all()
client = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
bot = commands.Bot(command_prefix=prefix, intents=intents, case_insensitive=True)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Invite bot link to discord (open in browser):\nhttps://discord.com/api/oauth2/authorize?client_id='+ str(bot.user.id) +'&permissions=8&scope=bot\n')
    while True:
        update_settings()
        try:
            operations = ''
            operations = await check_operations()
            if operations['responce']['status'] == 'ok':
                await get_traid(operations)
            else:
                print("Ошибка. Статус не 'ok'.")
        except Exception as e:
            print(f'Failed to get operations\n {e}')

        await asyncio.sleep(int(timer))

##################################################
##					COMMANDS					##
@bot.slash_command(description="Show commands list")
async def help(ctx):
    await ctx.send('**==Support commands==**\n'
                   f' Показать список комманд: ```{prefix}help```\n'
                   f' **Need admin rights**\n'
                   f' Показать список сопоставлений: ```{prefix}list```\n'
                   f' Добавить сопоставление: ```{prefix}addoffer offer_id server_id name```\n'
                   f' Удалить сопоставление: ```{prefix}deloffer offer_id```',
                   ephemeral=True
                   )

@bot.slash_command(description="Сопоставить ИД предложения с ИД сервера")
async def addoffer(ctx: disnake.ApplicationCommandInteraction, offer_id: int, server_id: int, name: str):
    if ctx.author.guild_permissions.administrator:
        try:
            await write_cfg('server', f'{offer_id}', f'{server_id}: {name}')
            update_settings()

            await ctx.response.send_message(f'Добавлено сопоставление:\n {offer_id} = {server_id}: {name}', ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f'❌ Не удалось добавить сопоставление.', ephemeral=True)
            print(f'Error occurred during file write: {e}')
    else:
        await ctx.response.send_message("❌ You do not have permission to run this command.", ephemeral=True)

@bot.slash_command(description="Удалить ИД предложения")
async def deloffer(ctx: disnake.ApplicationCommandInteraction, offer_id: int):
    if ctx.author.guild_permissions.administrator:
        try:
            offer = None
            for key, value in lists.items():
                if int(key) == offer_id:
                    offer = f'{key} = {value}'
                    break
            if offer:
                await del_cfg('server', f'{offer_id}')
                await ctx.response.send_message(f'Удалено сопоставление:\n{offer}', ephemeral=True)
            else:
                await ctx.response.send_message(f'❌ Не найдено сопоставление:\n{offer_id}', ephemeral=True)

        except Exception as e:
            await ctx.response.send_message('❌ Не удалось удалить сопоставление.', ephemeral=True)
            print(f'❌ Произошла ошибка при удалении сопоставления: {e}')
        update_settings()
    else:
        await ctx.response.send_message("❌ У вас нет разрешения на выполнение этой команды.", ephemeral=True)

@bot.slash_command(description="Показать список сопоставленных товаров и серверов")
async def list(ctx):
    if ctx.author.guild_permissions.administrator:
        update_settings()
        list = '\n'.join([f'{key} = {value}' for key, value in lists.items()])
        await ctx.send(f'Список сопоставленных предложений с серверами:\n{list}', ephemeral=True)
    else:
        await ctx.response.send_message("❌ You do not have permission to run this command.", ephemeral=True)

@bot.slash_command(description="Канал оповещения")
async def sendhere(ctx: disnake.ApplicationCommandInteraction):
    if ctx.author.guild_permissions.administrator:
        try:
            guild = ctx.guild
            print(f'New channel id - {ctx.channel.id}')
            await write_cfg('botconfig', 'channel_id', str(ctx.channel.id))
            await guild.fetch_channel(ctx.channel.id)
            await ctx.response.send_message(content=f'Этот канал установлен в качестве оповещений', ephemeral=False)
            update_settings()
        except Exception as e:
            await ctx.response.send_message(content='❌ An error occurred. Please try again later.', ephemeral=True)
            print(f'Error occurred during file write: {e}')
    else:
        await ctx.response.send_message(content='❌ You do not have permission to run this command.', ephemeral=True)

##################################################
##					START BOT					##
try:
    bot.run(bot_token)
except disnake.errors.LoginFailure:
    print(' Improper bot_token has been passed.\n Get valid app bot_token https://discord.com/developers/applications/ \nscreenshot https://junger.zzux.com/webhook/guide/4.png')
except disnake.HTTPException:
    print(' HTTPException Discord API')
except disnake.ConnectionClosed:
    print(' ConnectionClosed Discord API')
except disnake.errors.PrivilegedIntentsRequired:
    print(' Privileged Intents Required\n See Privileged Gateway Intents https://discord.com/developers/applications/ \nscreenshot http://junger.zzux.com/webhook/guide/3.png')
