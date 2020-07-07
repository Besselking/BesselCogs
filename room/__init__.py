from .room import Room


def setup(bot):
    n = Room(bot)
    bot.add_cog(n)
