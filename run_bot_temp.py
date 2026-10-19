
import sys
sys.path.insert(0, r'C:\Users\pierr\Desktop\Fistiniere Projet\FistiBot')
try:
    import bot
except Exception as e:
    print(f"ERREUR: {e}")
    import traceback
    traceback.print_exc()
    input("Appuie sur Entrée pour fermer...")
