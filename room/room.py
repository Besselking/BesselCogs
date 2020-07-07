from redbot.core import commands, Config
import re

class Room(commands.Cog):
    """Zure room is mijn faventer"""

    room_words = [
            "room",
            "zure",
            "zuur",
            "fav",
            "favo",
            "faventer",
            "favoriet",
    ]

    re_room = []
    
    def __init__(self,bot):
        self.bot = bot
        self.re_room  = [self._find_word(x) for x in self.room_words]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        msg = message.content
        

        if any(1 for reg in self.re_room if reg(msg)):
            await message.channel.send("Zure room is mijn faventer")
        

    def _find_word(self, word):
        return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search
    
