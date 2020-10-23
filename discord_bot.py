#!/usr/bin/env python3

import logging, discord, asyncio, time, re
import googletrans, pickle, sys, os
import discord_bot_config as botconfig
import hashlib, traceback, json
from discord.ext import commands as discord_cmd
from pprint import pprint
from kooking_purchases import kooking_purchases, get_purchases
from datetime import datetime

try: out_file = sys.argv[1]
except: out_file = 'kooking.data'
try: basedir = sys.argv[2]
except: basedir = '.'
logging_handler = logging.StreamHandler(stream = sys.stdout)
logging.basicConfig(level = logging.INFO,
                    format = "%(asctime)s [%(levelname)s] %(message)s",
                    #handlers = [logging.FileHandler('%s/discord_bot.log' % basedir)],
                    handlers = [logging_handler])

bot = discord_cmd.Bot(command_prefix = '!', case_insensitive = True)
re_user = re.compile(r'[<][@][!]?\s*([0-9]+)[>]')
purchases_task_created = 0

@bot.event
async def on_ready():
    global purchases_task_created
    logging.info("bot ready")
    purchases_task_created += 1
    old_purchases_task_created = purchases_task_created
    try:
        with open('%s/printed_purchases.dat' % basedir, 'rb') as fd:
            printed_purchases = pickle.load(fd)
    except: printed_purchases = set()
    channel = bot.get_channel(745982903686529155)
    while purchases_task_created == old_purchases_task_created:
        try:
            kooking_data = kooking_purchases(get_purchases())
            with open(out_file + '.tmp', 'w', encoding = 'utf-8') as fd:
                json.dump(kooking_data, fd, ensure_ascii = False)
            os.rename(out_file + '.tmp', out_file)
            for purchase in kooking_data:
                if purchase['purchase'] not in printed_purchases:
                    try:
                        try: ts = datetime.strptime(purchase['ts'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%H:%M')
                        except:
                            ts = datetime.strptime(purchase['ts'], '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M')
                        if len(purchase.get('comment', '')) > 0:
                            comment = f", {purchase['comment']}"
                        else: comment = ''
                        if len(purchase.get('description', '')) > 0:
                            description = f" ({purchase['description']})"
                        else: description = ''
                        if len(purchase.get('variant_name', '')) > 0:
                            variant = f":{purchase['variant_name']}"
                        else: variant = ''
                        await channel.send(f"{ts} {purchase['name']}{variant}{comment}{description} count:{purchase['quantity']}", delete_after = 60*60)
                    except Exception as err:
                        logging.exception('Could not send the purchase message!')
                printed_purchases.add(purchase['purchase'])
                with open('%s/printed_purchases.tmp' % basedir, 'wb') as fd:
                    pickle.dump(printed_purchases, fd)
                os.rename('%s/printed_purchases.tmp' % basedir, '%s/printed_purchases.dat' % basedir)
        except Exception as err:
            logging.exception('Handling purchases got an error!')
        sys.stdout.flush()
        await asyncio.sleep(5)

@bot.event
async def on_message(message):
    msg = str(message.content).strip()
    msg = msg.replace('https://', '').replace('http://', '')
    users_to_replace = set()
    for ma_user in re_user.finditer(msg):
        uid = int(ma_user.group(1))
        user = message.guild.get_member(uid)
        users_to_replace.add((uid, user.name))
    if msg.startswith('TTTS'):
        ttts = True
        msg = msg[4:].strip()
    else: ttts = False
    if not message.author.bot and len(msg) > 4:
        try:
            msg_en = googletrans.Translator().translate(msg, dest = 'en').text
            msg_no = googletrans.Translator().translate(msg, dest = 'no').text
            for uid, name in users_to_replace:
                msg = re.sub(f'[<][@][!]? *{uid} *[>]', name, msg)
                msg_en = re.sub(f'[<][@][!]? *{uid} *[>]', name, msg_en)
                msg_no = re.sub(f'[<][@][!]? *{uid} *[>]', name, msg_no)
            logging.info(f'{msg=} {msg_no=} {msg_en=}')
            if msg_no.lower().strip() != msg.lower().strip():
                await message.channel.send(f"{message.author.name}: {msg_no}", delete_after = 60*60, tts = ttts)
            elif msg_en.lower().strip() != msg.lower().strip():
                await message.channel.send(f"{message.author.name}: {msg_en}", delete_after = 60*60, tts = ttts)
        except Exception as err:
            logging.exception('Could not translate the message!')

bot.run(botconfig.DISCORD_TOKEN)
