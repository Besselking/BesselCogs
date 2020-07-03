from collections import defaultdict
from redbot.core import Config, commands, checks

import discord
import numpy as np


class ConnectFour(commands.Cog):
    """My custom cog"""

    numbers = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣"]

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1341493164132151357)
        default_guild = {
            "empty_cell": ":blue_square:",
            "red_cell": ":red_circle:",
            "yellow_cell": ":yellow_circle:",
        }

        self.config.register_guild(**default_guild)

        self.the_data = defaultdict(
            lambda: {
                "red_turn": True,
                "red_pieces": 0,
                "yellow_pieces": 0,
                "trackmessage": False,
                "red_player": None,
                "yellow_player": None,
            }
        )

        self.winbool = defaultdict(lambda: False)

    @commands.group(aliases=["setconnect4"])
    @checks.mod_or_permissions(administrator=True)
    async def connect4set(self, ctx, empty, red, yellow):
        """Adjust Connect Four settings"""
        message = ctx.message
        for k, x in {"empty": empty, "red": red, "yellow": yellow}.items():
            if x[:2] == "<:":
                x = self.bot.get_emoji(int(x.split(":")[2][:-1]))

            if x is None:
                await ctx.send("I could not find that emoji")
                return

            try:
                # Use the face as reaction to see if it's valid (THANKS FLAPJACK <3)
                await message.add_reaction(x)
            except discord.errors.HTTPException:
                await ctx.send("That's not an emoji I recognize.")
                return

            await self.config.guild(ctx.guild).get_attr("{}_cell".format(k)).set(str(x))
            await ctx.send("{} cell emoji has been updated!".format(k.capitalize()))

    @connect4set.command()
    async def empty(self, ctx: commands.Context, theemoji):
        """Set the emoji of an empty cell"""
        message = ctx.message

        if theemoji[:2] == "<:":
            theemoji = self.bot.get_emoji(int(theemoji.split(":")[2][:-1]))

        if theemoji is None:
            await ctx.send("I could not find that emoji")
            return

        try:
            # Use the face as reaction to see if it's valid (THANKS FLAPJACK <3)
            await message.add_reaction(theemoji)
        except discord.errors.HTTPException:
            await ctx.send("That's not an emoji I recognize.")
            return

        await self.config.guild(ctx.guild).empty_cell.set(str(theemoji))
        await ctx.send("Empty cell has been updated!")

    @connect4set.command()
    async def red(self, ctx: commands.Context, theemoji):
        """Set the emoji of an red cell"""
        message = ctx.message

        if theemoji[:2] == "<:":
            theemoji = self.bot.get_emoji(int(theemoji.split(":")[2][:-1]))

        if theemoji is None:
            await ctx.send("I could not find that emoji")
            return

        try:
            # Use the face as reaction to see if it's valid (THANKS FLAPJACK <3)
            await message.add_reaction(theemoji)
        except discord.errors.HTTPException:
            await ctx.send("That's not an emoji I recognize.")
            return

        await self.config.guild(ctx.guild).red_cell.set(str(theemoji))
        await ctx.send("Red cell has been updated!")

    @connect4set.command()
    async def yellow(self, ctx: commands.Context, theemoji):
        """Set the emoji of an yellow cell"""
        message = ctx.message

        if theemoji[:2] == "<:":
            theemoji = self.bot.get_emoji(int(theemoji.split(":")[2][:-1]))

        if theemoji is None:
            await ctx.send("I could not find that emoji")
            return

        try:
            # Use the face as reaction to see if it's valid (THANKS FLAPJACK <3)
            await message.add_reaction(theemoji)
        except discord.errors.HTTPException:
            await ctx.send("That's not an emoji I recognize.")
            return

        await self.config.guild(ctx.guild).yellow_cell.set(str(theemoji))
        await ctx.send("Yellow cell has been updated!")

    @commands.command()
    async def connect4(self, ctx: commands.Context, opponent: discord.Member):
        """Play a game of Connect Four against another player"""
        if opponent is None:
            await ctx.send(
                "Mention someone to play against `{}connect4 <mention>`".format(
                    ctx.prefix
                )
            )
        else:
            await ctx.send("Starting a game of Connect Four")
            self._startgame(ctx.guild, ctx.author, opponent)
            await self._printgame(ctx.channel)

    def _startgame(self, guild, red_user, yellow_user):
        """Starts a new game of Connect Four"""
        self.the_data[guild]["red_turn"] = True
        self.the_data[guild]["pieces"] = np.full((5, 7, 2), False)
        self.the_data[guild]["trackmessage"] = False
        self.the_data[guild]["red_player"] = red_user
        self.the_data[guild]["yellow_player"] = yellow_user
        self.winbool[guild] = False

    async def _insert_in_column(self, column, message):
        """Inserts a disk into the given column and prints the game"""
        channel = message.channel
        guild = channel.guild
        guild_data = self.the_data[guild]
        pieces = guild_data["pieces"]
        red_turn = guild_data["red_turn"]

        for rn, row in enumerate(reversed(pieces)):
            r, y = row[column - 1]
            if not (r or y):
                p = int(not red_turn)
                pieces[-rn - 1][column - 1][p] = True
                break

        self.the_data[guild]["red_turn"] = not red_turn

        self.the_data[guild]["pieces"] = pieces

        await message.edit(content=await self._make_say(guild))

    @commands.Cog.listener()
    async def on_react(self, reaction, user):
        if reaction.message.id != self.the_data[user.guild]["trackmessage"]:
            return

        if user == self.bot.user:
            return

        guild_data = self.the_data[user.guild]
        if not (user == guild_data["red_player"] and guild_data["red_turn"]) and not (
            user == guild_data["yellow_player"] and not guild_data["red_turn"]
        ):
            return

        message = reaction.message
        emoji = reaction.emoji

        if str(emoji) in self.numbers:
            number = int("1234567"[self.numbers.index(str(emoji))])
            await self._insert_in_column(number, message)
            await message.remove_reaction(emoji, user)

    async def _reactmessage_menu(self, message):
        """React with menu options"""
        for number in range(len(self.numbers)):
            await message.add_reaction(self.numbers[number])

    async def _make_say(self, guild):
        guild_data = self.the_data[guild]
        pieces = guild_data["pieces"]
        guild_conf = self.config.guild(guild)
        red_cell = await guild_conf.red_cell()
        yellow_cell = await guild_conf.yellow_cell()
        empty_cell = await guild_conf.empty_cell()

        board = ["".join(self.numbers), "\n"]
        for row in pieces:
            for piece in row:
                if piece[0]:
                    board.append(red_cell)
                elif piece[1]:
                    board.append(yellow_cell)
                else:
                    board.append(empty_cell)
            board.append("\n")
        board.append("".join(self.numbers))

        red_player = guild_data["red_player"]
        yellow_player = guild_data["yellow_player"]
        red_turn = guild_data["red_turn"]

        board.append(
            "\n\n{}{}{}".format(
                red_cell, red_player.mention, "'s turn" if red_turn else ""
            )
        )
        board.append(
            "\n{}{}{}".format(
                yellow_cell, yellow_player.mention, "'s turn" if not red_turn else ""
            )
        )
        return "".join(board)

    async def _printgame(self, channel):
        """Print the current state of the game"""

        message = await channel.send(content=await self._make_say(channel.guild))

        self.the_data[channel.guild]["trackmessage"] = message.id

        await self._reactmessage_menu(message)
