#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, r'C:\Users\pierr\Desktop\Fistiniere Projet\FistiBot')
os.chdir(r'C:\Users\pierr\Desktop\Fistiniere Projet\FistiBot')

print("=" * 60)
print("Démarrage du FistiBot...")
print("=" * 60)
print()

try:
    # Importer et lancer bot.py
    exec(open('bot.py').read())
except KeyboardInterrupt:
    print()
    print("Bot arrêté par l'utilisateur")
except Exception as e:
    print()
    print("=" * 60)
    print("ERREUR:")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)

print("Appuie sur Entrée pour fermer la fenêtre...")
input()
