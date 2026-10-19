from discord.ext import tasks
from datetime import date
from newRiotPart import whichIconRank, whichIcon, riot, fis
from matplotlib.pyplot import title
from utils import send_long
from config import *


class RiotTasks:
    def __init__(self, bot):
        self.bot = bot
        # self.daily_update.start()
        self.test_update.start()

    async def build_ranking(self, queue):
        # Les données sont mises à jour par les tâches planifiées (daily_update, test_update)
        # On affiche juste ce qui est dans le JSON sans re-mettre à jour
        
        # Recharger les données du JSON (au cas où elles auraient été mises à jour)
        fis.load()
        data = fis.data[queue]

        today = date.today().strftime("%d/%m/%Y")
        title = "LoL" if queue == "RANKED_SOLO_5x5" else "TFT"

        msg = f"Classement sur {title} de la Fistinière du {today}\n\n"

        # Trier par rank (en utilisant la fonction rank_score)
        from newRiotPart import rank_score
        sorted_data = sorted(
            data.items(),
            key=lambda x: rank_score((x[1]["rank"]["tier"], x[1]["rank"]["div"], x[1]["rank"]["lp"])),
            reverse=True
        )

        for i, (name, player) in enumerate(sorted_data, start=1):
            rank = player["rank"]
            
            if i < 10:
                number = f":number_{i}:"
            else:
                tens = f":number_{i // 10}:"
                ones = f":number_{i % 10}:"
                number = tens + ones

            msg += (
                f"{number} {name} "
                f"{whichIconRank(rank['tier'])} "
                f"{rank['tier']} {rank['div']} "
                f"{rank['lp']} LP "
                f"({rank['lpDeltaDaily']} LP depuis hier {whichIcon(rank['lpDeltaDaily'])})\n"
            )

        return msg

    @tasks.loop(hours=24)
    async def daily_update(self):
        # Recharger les données fraiches du JSON avant de mettre à jour
        fis.load()
        # Mise à jour des données depuis l'API
        await fis.update_all(riot)
        
        ch = self.bot.get_channel(CHANNEL_MAIN)
        if ch:
            # On rebuild après update
            msg = await self.build_ranking("RANKED_SOLO_5x5")
            await send_long(ch, msg, MAX_DISCORD_LEN)
        ch_tft = self.bot.get_channel(CHANNEL_TFT)
        if ch_tft:
            msg = await self.build_ranking("RANKED_TFT")
            await send_long(ch_tft, msg, MAX_DISCORD_LEN)

    @tasks.loop(hours=24)
    async def test_update(self):
        # Recharger les données fraiches du JSON avant de mettre à jour
        fis.load()
        # Mise à jour des données depuis l'API
        await fis.update_all(riot)
        
        ch = self.bot.get_channel(CHANNEL_TEST)
        if ch:
            # On rebuild après update
            msg = await self.build_ranking("RANKED_SOLO_5x5")
            msg += "\n" + await self.build_ranking("RANKED_TFT")
            await send_long(ch, msg, MAX_DISCORD_LEN)
