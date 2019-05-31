from nonebot import on_command, CommandSession, logger
from nonebot.typing import *

import nonebot

bot = nonebot.get_bot()

@on_command('intro-bot', aliases=())
async def weather(session: CommandSession):
    msg = """ QQ Chat Bot @ Chuibility. Commands availabe
    - /intro-bot Display this message
    - /echo      Echos the content
    - /cgcalc    Invokes the Lispy Calculator
    * [Repeater] If the messeage is received 3 or more times, repeats it.

    ('*' items does not have a command corresponding to it) 
    
    It is important to emphasize that altough some features requires the bot to constantly \
    monitoring all communication, we specifically made a design choice NOT to record any of\
    them. We want to create a safe environment for everyone. However, commands explicitly \
    directed to the bot may be logged."""
    await session.send(msg)
