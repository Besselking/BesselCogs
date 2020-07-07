from redbot.core import commands

from discord.player import FFmpegAudio
import discord
import shlex
import subprocess

class Spotifyd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, * channel: discord.VoiceChannel):
        if ctx.author.voice.channel is not None:
            return await ctx.author.voice.channel.connect()

        await channel.connect()

    @commands.command()
    async def splay(self, ctx):
        source = discord.PCMVolumeTransformer(FFmpegAlsaAudio('alsa_output.pci-0000_00_1f.3.analog-stereo.monitor'))
        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)


class FFmpegAlsaAudio(FFmpegAudio):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        args = []
        subprocess_kwargs = {'stdin': source if pipe else subprocess.DEVNULL, 'stderr': stderr}

        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))

        args.extend(('-f', 'pulse'))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le'))
        args.extend(( '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))

        if isinstance(options, str):
            args.extend(shlex.split(options))

        args.append('pipe:1')

        print(str(args))

        super().__init__(source, executable=executable, args=args, **subprocess_kwargs)

    def read(self):
        ret = self.__stdout.read(OpusEncoder.FRAME_SIZE)
        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

    def is_ipus(self):
        return False
