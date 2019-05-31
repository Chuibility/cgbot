from nonebot import on_command, CommandSession, logger
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.typing import *

import nonebot, sys

bbks = dict()

bot = nonebot.get_bot()

def log(msg):
    logger.debug(msg);

log("test log")

@bot.on_message('group')
async def handle_group_message(ctx : Context_T):
    self_id = ctx['self_id']
    user_id = ctx['group_id']
    msg = ctx['raw_message']
    if bbks.get(user_id) is None:
        log(f"New bbk discovered, id = {user_id}")
        bbks[user_id] = (1, msg)
    else:
        (count, lastMsg) = bbks[user_id]
        if lastMsg == msg:
            log(f"{user_id} repeated {msg}")
            count += 1
            bbks[user_id] = (count, msg)
            if count == 3:
                log(f"{user_id} msg time: {msg}")
                await bot.send(ctx, msg)
        else:
            log(f"new message {user_id}")
            bbks[user_id] = (1, msg)

@on_command('repeater', aliases=())
async def weather(session: CommandSession):
    msg = session.state.get("msg");
    #user = session.state.get("user");
    #await debug_send(session, 'debug')
    #await session.send(f'{user} - repeater: {msg}')
    await session.send(msg)

@on_natural_language()
async def _(session: NLPSession):
    user_id = session.ctx['user_id']
    msg = session.msg
    if bbks.get(user_id) is None:
        bbks[user_id] = (1, msg)
        # await debug_send(session, f"New bbk discovered, id = {user_id}")
    else:
        (count, lastMsg) = bbks[user_id]
        if lastMsg == msg:
            count += 1
            bbks[user_id] = (count, msg)
            if count == 3:
                return IntentCommand(100.0, 'repeater', 
                        args= { 
                            "msg" : msg, 
                            "user" : user_id 
                            }
                        )
        else:
            bbks[user_id] = (1, msg)
    return IntentCommand(0.00, 'repeater')
