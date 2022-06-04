#WaLLE
import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


#** Commands **#
#** YoutubeDL **#
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # pega o primeiro item da playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename



@bot.command(name='claudinei')
async def play(ctx,url):
    try :
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Tocando Agora:** {}'.format(filename))
    except:
        await ctx.send("Ocorreu algum problema ao tocar isso, será que eu estou mesmo no canal de voz?")


@bot.command(name='entrar')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} não está conectado no canal de voz".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='pausar')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("Eu não posso pausar, pois não está tocando nada, me desculpe :(")
    
@bot.command(name='resumir')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("Eu não estava tocando nada antes de ser pausado, então não posso continuar :(")
    


@bot.command(name='sair')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Eu não estou conectado a nenhum canal de voz, então não posso sair :(")

@bot.command(name='parar')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("Eu não estou tocando nada agora, não me manda parar, por favor :(")




#? : Filtrar palavras da mensagem do usuário
@bot.event
async def on_message(message) :
    await bot.process_commands(message) 
    if str(message.content).lower() in ['swear_word1','swear_word2']:
        await message.channel.purge(limit=1)





#? :Iniciar Aplicação
if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)