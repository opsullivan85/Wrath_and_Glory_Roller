from discord.ext import commands
import discord_slash
from discord_slash import SlashCommand
import os
from dotenv import load_dotenv
from pathlib import Path
import wrath_and_glory_roller
import logging
import re
from random import randint
from io import StringIO

# load .env file from parent directory
parent_path = Path(wrath_and_glory_roller.__path__[0]).parent
load_dotenv(dotenv_path=parent_path.joinpath('.env').__str__())

client = commands.Bot(command_prefix="prefix")
slash = SlashCommand(client, sync_commands=True)  # Declares slash commands through the client.

regex = r"(?:([+\-]?) *(\d+) *d *(\d+))|(?:([+\-*/]?) *(\d+))"

logging.basicConfig(level=logging.INFO, filename=parent_path.joinpath('logfile.log').__str__(),
                    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w')


@client.event
async def on_ready():
    print("Ready!")


def eval_sign(sign: str) -> int:
    if sign in ['', '+']:
        return 1
    elif sign == '-':
        return -1


def eval_roll(roll: int) -> int:
    if roll <= 3:
        return 0
    elif roll <= 5:
        return 1
    else:
        return 2


@slash.slash(name="roll",
             description='Roll some dice',
             options=[
                 {
                     'name': 'rolling_string',
                     'description': 'The roll to evaluate',
                     'type': 3,  # string
                     'required': True
                 }
             ])
async def _roll(ctx: discord_slash.context.SlashContext,
                rolling_string: str):  # Defines a new "context" (ctx) command called "ping."
    matches = re.findall(regex, rolling_string)
    logging.info('in _roll():\n'
                 f'\t{ctx.command = }\n'
                 f'\t{rolling_string = }\n'
                 f'\t{matches = }\n'
                 f'\t{ctx.channel = }\n'
                 f'\t{ctx.author = }')
    if len(matches) > 0:

        msg = StringIO()
        msg.write('Result: ')

        total = 0

        for match in matches:
            if match[1]:  # non-constant
                sign, rolls, dice, *_ = match

                if sign:
                    msg.write(sign)
                    msg.write(' ')

                msg.write(rolls)
                msg.write('d')
                msg.write(dice)
                msg.write('(')

                sign = eval_sign(sign)
                rolls = int(rolls)
                dice = int(dice)

                if rolls > 25:
                    await ctx.send('You cannot roll more than 25 dice', hidden=True)
                    return

                for i in range(rolls):
                    roll = randint(1, dice)
                    msg.write(str(roll))
                    if i < rolls - 1:
                        msg.write(', ')
                    total += sign * eval_roll(roll)
                msg.write(') ')

            else:  # constant
                *_, sign, num = match

                if sign:
                    msg.write(sign)
                    msg.write(' ')

                msg.write(num)
                msg.write(' ')

                sign = eval_sign(sign)
                num = int(num)

                total += sign * num

        msg.write(f'\nTotal: {total}')
        await ctx.send(msg.getvalue())
    else:
        await ctx.send('Could not parse your command, try something like "3d6 + 2"', hidden=True)


client.run(os.getenv('TOKEN'))
