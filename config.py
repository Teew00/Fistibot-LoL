from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CHANNEL_MAIN = int(os.getenv("CHAN_ID"))
CHANNEL_TEST = int(os.getenv("CHAN_ID_TEST"))
CHANNEL_TFT = int(os.getenv("CHAN_ID_TFT"))

MAX_DISCORD_LEN = 1990
