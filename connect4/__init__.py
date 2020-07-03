from .connect4 import ConnectFour
from redbot.core import data_manager


def setup(bot):
    n = ConnectFour(bot)
    bot.add_cog(n)
    bot.add_listener(n.on_react, "on_reaction_add")
