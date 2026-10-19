from discord.ext import commands
import newRiotPart as riotPart

class RiotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def rank(self, ctx, game_name: str, tag_line: str):
        solo, tft = await riotPart.myRank(game_name, tag_line)

        msg = (
            f"{game_name} : {riotPart.whichIconRank(solo['tier'])} "
            f"{solo['tier']} {solo['rank']} ({solo['lp']} LP)\n"
            f"TFT : {riotPart.whichIconRank(tft['tier'])} "
            f"{tft['tier']} {tft['rank']} ({tft['lp']} LP)"
        )

        await ctx.send(msg)

    @commands.command()
    async def addplayer(self, ctx, *, game_info: str):
        parts = game_info.split()
        if len(parts) < 2:
            await ctx.send("❌ Format: `!addplayer <game_name> <tag_line>`")
            return
        
        # Le dernier élément est le tag_line, le reste est le game_name
        tag_line = parts[-1].strip('"\'')
        game_name = " ".join(parts[:-1]).strip('"\'')

        if not game_name.startswith("FIS"):
            await ctx.send("❌ Tu dois être un FIS.")
            return
        
        try:
            await ctx.send("⏳ Ajout du joueur...")
            result = await riotPart.fis.add_player(game_name, tag_line, riotPart.riot)
            print(f"Résultat: {result}")
            await ctx.send(result)
        except Exception as e:
            print(f"Erreur addplayer: {e}")
            await ctx.send(f"❌ Erreur: {str(e)}")