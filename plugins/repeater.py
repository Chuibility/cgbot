from nonebot import on_command, CommandSession, logger
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.typing import *

import nonebot, sys

import handlers
import orm

bot = nonebot.get_bot()

@handlers.on_GroupMsg("repeater")
async def test(ctx, user : orm.User, group, user_in_group, state : dict):
    msg = ctx['raw_message']
    count = state.setdefault("count", 0)
    lastMsg = state.setdefault("lastMsg", msg)
    if lastMsg == msg:
        count += 1
        if count == 3:
            await bot.send(ctx, msg)
    else:
        count = 1
    state["count"] = count
    state["lastMsg"] = msg