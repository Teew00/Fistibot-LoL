from pathlib import Path
from wsgiref import headers
from dotenv import load_dotenv
import requests
from riotwatcher import LolWatcher, RiotWatcher, ApiError
import os, json
import aiohttp
import asyncio

# =====================
# CONFIGURATION
# =====================

BASE_PATH = Path(__file__).parent
load_dotenv(BASE_PATH / ".env")

LOL_API_KEY = os.getenv("RIOT_API_KEY")
TFT_API_KEY = os.getenv("TFT_API_KEY")

REGION_LOL = "euw1"
REGION_ACCOUNT = "europe"

DATA_PATH = BASE_PATH / "fisList.json"

TIERS = [
    "UNRANKED","IRON","BRONZE","SILVER","GOLD",
    "PLATINUM","EMERALD","DIAMOND",
    "MASTER","GRANDMASTER","CHALLENGER"
]

DIVS = {"IV": 0, "III": 1, "II": 2, "I": 3}
MASTER_PLUS = {"MASTER", "GRANDMASTER", "CHALLENGER"}

class RiotService:
    def __init__(self):
        self.lol = LolWatcher(LOL_API_KEY)
        self.riot = RiotWatcher(LOL_API_KEY)

    # ---------- ACCOUNT ----------
    def get_puuids(self, game_name, tag_line):
        acc = self.riot.account.by_riot_id(REGION_ACCOUNT, game_name, tag_line)
        acc_tft = RiotWatcher(TFT_API_KEY).account.by_riot_id(
            REGION_ACCOUNT, game_name, tag_line
        )
        return acc["puuid"], acc_tft["puuid"]

    # ---------- LOL ----------
    def get_lol_rank(self, puuid):
        try:
            ranks = self.lol.league.by_puuid(REGION_LOL, puuid)
            return next(
                (r for r in ranks if r["queueType"] == "RANKED_SOLO_5x5"),
                None
            )
        except ApiError:
            return None

    # ---------- TFT (HTTP DIRECT) ----------
    async def get_tft_rank_async(self, puuid, debug=False):
        """Fetch TFT rank from the /by-puuid endpoint which returns player data directly"""
        url = f"https://euw1.api.riotgames.com/tft/league/v1/by-puuid/{puuid}"
        headers = {"X-Riot-Token": TFT_API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    if debug:
                        print(f"  [TFT] API returned {resp.status}")
                    return None
                    
                leagues = await resp.json()  # This is a list of league objects
                if debug:
                    print(f"  [TFT] Got {len(leagues)} queue(s)")
                
                # Find RANKED_TFT (not DOUBLE_UP or other variants)
                for league in leagues:
                    if league.get("queueType") == "RANKED_TFT":
                        if debug:
                            tier = league.get("tier", "UNRANKED")
                            rank = league.get("rank", "")
                            lp = league.get("leaguePoints", 0)
                            print(f"  [TFT] Found RANKED_TFT: {tier} {rank}, {lp} LP")
                        
                        return {
                            "tier": league.get("tier", "UNRANKED"),
                            "rank": league.get("rank", ""),
                            "leaguePoints": league.get("leaguePoints", 0)
                        }
                
                if debug:
                    print(f"  [TFT] RANKED_TFT not found. Available: {[l.get('queueType') for l in leagues]}")
                return None
            
class FisManager:
    def __init__(self):
        self.data = {"RANKED_SOLO_5x5": {}, "RANKED_TFT": {}}
        self.path = Path("fisList.json")
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def load(self):
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    async def add_player(self, game_name, tag_line, riot: RiotService):
        if game_name in self.data["RANKED_SOLO_5x5"]:
            return f"{game_name} est déjà dans la liste."

        try:
            puuid_lol, puuid_tft = riot.get_puuids(game_name, tag_line)

            lol_rank = riot.get_lol_rank(puuid_lol)
            tft_rank = await riot.get_tft_rank_async(puuid_tft)

            self.data["RANKED_SOLO_5x5"][game_name] = self.format_rank(puuid_lol, lol_rank)
            self.data["RANKED_TFT"][game_name] = self.format_rank(puuid_tft, tft_rank)

            self.save()
            return f"✅ {game_name} ajouté avec succès."
        except Exception as e:
            return f"❌ Erreur: {str(e)}"

    def format_rank(self, puuid, rank):
        if not rank:
            return {
                "puuid": puuid,
                "rank": {
                    "tier": "UNRANKED",
                    "div": "",
                    "lp": 0,
                    "lpDeltaDaily": 0,
                    "lpDeltaForever": 0
                }
            }

        return {
            "puuid": puuid,
            "rank": {
                "tier": rank["tier"],
                "div": rank.get("rank", ""),
                "lp": rank["leaguePoints"],
                "lpDeltaDaily": 0
            }
        }

    async def update_all(self, riot_service):
        for queue in ["RANKED_SOLO_5x5", "RANKED_TFT"]:
            print(f"\n[*] Mise à jour {queue}...")
            for player_name, player_data in self.data[queue].items():
                puuid = player_data["puuid"]

                try:
                    if queue == "RANKED_SOLO_5x5":
                        rank = await asyncio.to_thread(riot_service.get_lol_rank, puuid)
                    else:
                        rank = await riot_service.get_tft_rank_async(puuid, debug=False)

                    if rank:
                        # Mise à jour des ranks
                        old = player_data["rank"]
                        new_tier = rank.get("tier", "UNRANKED")
                        new_div = rank.get("rank", "")
                        new_lp = rank.get("leaguePoints", 0)
                        
                        # Pour TFT: calculer delta basé sur rank_score (comme LoL)
                        if queue == "RANKED_TFT":
                            old_score = rank_score((
                                old.get("tier", "UNRANKED"),
                                old.get("div", ""),
                                old.get("lp", 0)
                            ))
                            new_score = rank_score((new_tier, new_div, new_lp))
                            delta_daily = new_score - old_score
                            
                            player_data["rank"]["tier"] = new_tier
                            player_data["rank"]["div"] = new_div
                            player_data["rank"]["lp"] = new_lp
                            player_data["rank"]["lpDeltaDaily"] = delta_daily
                            
                            arrow = "UP" if delta_daily > 0 else "DOWN" if delta_daily < 0 else "FLAT"
                            print(f"[+] {player_name}: {new_tier} {new_div} - {new_lp} LP {arrow} ({delta_daily:+d})")
                        else:
                            # Pour LoL: calculer delta basé sur rank_score
                            old_score = rank_score((
                                old.get("tier", "UNRANKED"),
                                old.get("div", ""),
                                old.get("lp", 0)
                            ))
                            new_score = rank_score((new_tier, new_div, new_lp))
                            delta_daily = new_score - old_score
                            
                            player_data["rank"]["tier"] = new_tier
                            player_data["rank"]["div"] = new_div
                            player_data["rank"]["lp"] = new_lp
                            player_data["rank"]["lpDeltaDaily"] = delta_daily
                            
                            arrow = "UP" if delta_daily > 0 else "DOWN" if delta_daily < 0 else "FLAT"
                            print(f"[+] {player_name}: {new_tier} {new_div} - {new_lp} LP {arrow} ({delta_daily:+d})")
                    else:
                        # Pas de rang trouvé - mettre en UNRANKED
                        old = player_data["rank"]
                        old_score = rank_score((
                            old.get("tier", "UNRANKED"),
                            old.get("div", ""),
                            old.get("lp", 0)
                        ))
                        delta_daily = 0 - old_score
                        
                        player_data["rank"]["tier"] = "UNRANKED"
                        player_data["rank"]["div"] = ""
                        player_data["rank"]["lp"] = 0
                        player_data["rank"]["lpDeltaDaily"] = delta_daily
                        
                        if old.get("tier") != "UNRANKED":
                            print(f"[!] {player_name}: Passe a UNRANKED (inactif)")
                        
                except Exception as e:
                    print(f"[ERR] Erreur pour {player_name} ({queue}): {str(e)}")

        # Réécrire le JSON
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
        print(f"\n[OK] Mise à jour complète - {self.path} sauvegardé")

def safe_rank_diff(old_rank, new_rank):
    try:
        return rank_score(new_rank) - rank_score(old_rank)
    except Exception:
        return 0


def rank_score(rank):
    tier, div, lp = rank
    tier = tier.upper()

    if tier == "UNRANKED":
        return 0

    base = TIERS.index(tier) * 400

    if tier in MASTER_PLUS:
        return base + max(0, int(lp))

    return base + DIVS.get(div, 0) * 100 + min(max(int(lp), 0), 100)



ICON_PATH = Path(__file__).with_name("icons.json")

with open(ICON_PATH, "r", encoding="utf-8") as f:
    ICONS = json.load(f)


async def myRank(game_name, tag_line):
    riot = RiotService()
    puuid_lol, puuid_tft = riot.get_puuids(game_name, tag_line)
    
    lol_rank = riot.get_lol_rank(puuid_lol)
    tft_rank = await riot.get_tft_rank_async(puuid_tft)
    
    # Format pour retourner les données
    solo = {"tier": "UNRANKED", "rank": "", "lp": 0} if not lol_rank else {
        "tier": lol_rank.get("tier", "UNRANKED"),
        "rank": lol_rank.get("rank", ""),
        "lp": lol_rank.get("leaguePoints", 0)
    }
    
    tft = {"tier": "UNRANKED", "rank": "", "lp": 0} if not tft_rank else {
        "tier": tft_rank.get("tier", "UNRANKED"),
        "rank": tft_rank.get("rank", ""),
        "lp": tft_rank.get("leaguePoints", 0)
    }
    
    return solo, tft


def whichIconRank(tier: str) -> str:
    return ICONS.get(tier.upper(), "")


def whichIcon(diff: int) -> str:
    if diff > 0:
        return ICONS.get("UPARROW", "")
    if diff < 0:
        return ICONS.get("DOWNARROW", "")
    return ICONS.get("MIDARROW", "")


# Instances globales
riot = RiotService()
fis = FisManager()
