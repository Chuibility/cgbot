from nonebot import on_command, CommandSession, logger
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.typing import *

import nonebot, sys
import orm
import asyncio

_handlers = set()

_states = dict()

bot = nonebot.get_bot()

@bot.on_message('group')
async def msgHandler(ctx : Context_T):
    user_id = ctx['user_id']
    group_id = ctx['group_id']
    s = orm.getSession()
    user, _ = orm.getUserByidOrCreate(s, user_id)
    group, _ = orm.getGroupByIdOrCreate(s, group_id)
    user_in_group, _ = orm.getUserInGroupOrCreate(s, user, group)

    try:
        user_name = ctx['sender']['nickname']
        user_name_in_group = ctx['sender']['card']
    except KeyError:
        bot.logger.debug(ctx['sender'])
    else:
        if user.Name != user_name:
            bot.logger.debug(f"Changging name of {user_id} from {user.Name} to {user_name}")
            user.Name = user_name

        if user_in_group.Name != user_name_in_group:
            bot.logger.debug(f"Changging name of {user_id} in group {group_id} from {user_in_group.Name} to {user_name_in_group}")
            user_in_group.Name = user_name_in_group


    waits = []
    for (h, hg) in _handlers:
        # Each handler group shares a emphemeral state
        # Each different group have a different state object
        group_states = _states.setdefault(group_id, dict())
        state = group_states.setdefault(hg, dict())
        waits.append(h(ctx, user, group, user_in_group, state))

    await asyncio.wait(waits)

    bot.logger.debug(f"Committing changes (if any).")
    s.commit()
    s.close()

# Marks a handler as a group user message.
def on_GroupMsg(handler_group):
    def decor(handler):
        bot.logger.debug(f"Registering handler {handler} in group '{handler_group}'")
        _handlers.add((handler, handler_group))
        return handler
    return decor