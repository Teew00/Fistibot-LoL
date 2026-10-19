import tkinter as tk
from tkinter import ttk, messagebox
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv, set_key
import subprocess
import threading
import sys
import time

class BotLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FistiBot Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Déterminer le répertoire de base (exe ou script)
        if getattr(sys, 'frozen', False):
            # Si c'est un exe PyInstaller
            self.base_dir = Path(sys.executable).parent
        else:
            # Si c'est un script Python
            self.base_dir = Path(__file__).parent
        
        self.env_file = self.base_dir / ".env"
        self.bot_file = self.base_dir / "bot.py"
        
        print(f"Base directory: {self.base_dir}")
        print(f"Bot file exists: {self.bot_file.exists()}")
        
        self.load_env()
        self.setup_ui()
        
    def load_env(self):
        """Charger les valeurs actuelles du fichier .env"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        self.discord_token = os.getenv("DISCORD_TOKEN", "")
        self.riot_api_key = os.getenv("RIOT_API_KEY", "")
        self.tft_api_key = os.getenv("TFT_API_KEY", "")
    
    def setup_ui(self):
        """Créer l'interface utilisateur"""
        # Titre
        title = ttk.Label(self.root, text="Configuration FistiBot", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Discord Token
        ttk.Label(main_frame, text="Discord Token:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.discord_entry = ttk.Entry(main_frame, width=50, show="*")
        self.discord_entry.insert(0, self.discord_token)
        self.discord_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # Riot API Key
        ttk.Label(main_frame, text="Riot API Key:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.riot_entry = ttk.Entry(main_frame, width=50, show="*")
        self.riot_entry.insert(0, self.riot_api_key)
        self.riot_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)
        
        # TFT API Key
        ttk.Label(main_frame, text="TFT API Key:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tft_entry = ttk.Entry(main_frame, width=50, show="*")
        self.tft_entry.insert(0, self.tft_api_key)
        self.tft_entry.grid(row=2, column=1, sticky=tk.EW, padx=5)
        
        # Configure column weights
        main_frame.columnconfigure(1, weight=1)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Prêt à lancer", foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Save button
        save_btn = ttk.Button(button_frame, text="Sauvegarder", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Launch button
        launch_btn = ttk.Button(button_frame, text="Lancer le Bot", command=self.launch_bot)
        launch_btn.pack(side=tk.LEFT, padx=5)
        
        # Quit button
        quit_btn = ttk.Button(button_frame, text="Quitter", command=self.root.quit)
        quit_btn.pack(side=tk.LEFT, padx=5)
    
    def save_config(self):
        """Sauvegarder la configuration dans le fichier .env"""
        discord_token = self.discord_entry.get().strip()
        riot_api_key = self.riot_entry.get().strip()
        tft_api_key = self.tft_entry.get().strip()
        
        if not all([discord_token, riot_api_key, tft_api_key]):
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis!")
            return
        
        try:
            # Créer le fichier .env s'il n'existe pas
            if not self.env_file.exists():
                self.env_file.touch()
            
            # Sauvegarder les variables
            set_key(self.env_file, "DISCORD_TOKEN", discord_token)
            set_key(self.env_file, "RIOT_API_KEY", riot_api_key)
            set_key(self.env_file, "TFT_API_KEY", tft_api_key)
            
            self.status_label.config(text="✓ Configuration sauvegardée", foreground="green")
            messagebox.showinfo("Succès", "Configuration sauvegardée avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
            self.status_label.config(text="✗ Erreur lors de la sauvegarde", foreground="red")
    
    def launch_bot(self):
        """Lancer le bot"""
        # D'abord vérifier que tous les fichiers existent
        if not self.bot_file.exists():
            messagebox.showerror("Erreur", f"Fichier bot.py non trouvé!\n{self.bot_file}")
            return
        
        if not self.env_file.exists():
            messagebox.showerror("Erreur", f"Fichier .env non trouvé!\n{self.env_file}")
            return
        
        # Sauvegarder la config
        self.save_config()
        
        try:
            self.status_label.config(text="⏳ Lancement du bot...", foreground="blue")
            self.root.update()
            
            # Lancer le bot dans un thread séparé
            threading.Thread(target=self.run_bot, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du lancement: {str(e)}")
            self.status_label.config(text="✗ Erreur lors du lancement", foreground="red")
    
    def run_bot(self):
        """Exécuter le bot"""
        try:
            print(f"Launching bot from: {self.base_dir}")
            
            # Créer un script wrapper qui gère les erreurs et garde la console ouverte
            wrapper_script = f"""#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, r'{self.base_dir}')
os.chdir(r'{self.base_dir}')

print("=" * 60)
print("🤖 Démarrage de FistiBot...")
print("=" * 60)
print()

try:
    # Importer et lancer bot.py
    exec(open('bot.py').read())
except KeyboardInterrupt:
    print()
    print("⏹ Bot arrêté par l'utilisateur")
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERREUR:")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    print()
    print("=" * 60)

print("Appuie sur Entrée pour fermer la fenêtre...")
input()
"""
            
            script_file = self.base_dir / "_run_bot_wrapper.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(wrapper_script)
            
            # Chercher Python dans l'environnement virtuel
            python_exe = self.base_dir / ".venv" / "Scripts" / "python.exe"
            
            if not python_exe.exists():
                # Essayer d'autres chemins
                python_exe = Path(sys.executable)
            
            print(f"Utilisation de Python: {python_exe}")
            
            # Lancer le wrapper script
            result = subprocess.Popen(
                [str(python_exe), str(script_file)],
                cwd=str(self.base_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=None,  # Affiche la console naturellement
                stderr=None
            )
            
            self.status_label.config(text="✓ Bot lancé (regarde la console)", foreground="green")
            
        except Exception as e:
            error_msg = f"Erreur: {str(e)}"
            print(f"Erreur: {e}")
            messagebox.showerror("Erreur d'exécution", error_msg)
            self.status_label.config(text="✗ Erreur d'exécution", foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = BotLauncherGUI(root)
    root.mainloop()
