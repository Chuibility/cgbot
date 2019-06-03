from os import path

import nonebot
import config
import atexit
import orm

def commit_db():
    nonebot.logger.debug("Exiting. Commiting database changes...")
    orm.getSession().commit()

if __name__ == '__main__':
    atexit.register(commit_db)

    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'plugins'
    )
    nonebot.run()

