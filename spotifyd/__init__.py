from .spotifyd import Spotifyd


def setup(bot):
    n = Spotifyd(bot)
    bot.add_cog(n)
