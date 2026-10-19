# FistiBot

Bot Discord qui suit les classements **League of Legends (Solo/Duo)** et **Teamfight Tactics** des joueurs d'une structure, et publie chaque jour un classement avec l'évolution des LP de chacun.

---

## Fonctionnalités

- **Classement quotidien automatique** : toutes les 24 h, le bot récupère les rangs de tous les joueurs suivis via l'API Riot et poste un classement LoL et TFT sur Discord.
- **Suivi de progression** : pour chaque joueur, le gain ou la perte de LP depuis la veille est affiché avec une flèche ⬆️ / ⬇️ / ➡️.
- **Icônes de rang personnalisées** (Iron → Challenger) via des emojis Discord.
- **Commandes Discord** pour consulter un rang à la volée ou ajouter un joueur.
- **Lanceur graphique (GUI)** pour saisir les clés et démarrer le bot sans toucher au code.
- Découpage automatique des messages trop longs pour respecter la limite de Discord.

## Commandes

Préfixe : `!`

| Commande                    | Description                                                             | Exemple                        |
| --------------------------- | ----------------------------------------------------------------------- | ------------------------------ |
| `!rank <pseudo> <tag>`      | Affiche le rang LoL Solo/Duo et TFT d'un joueur                         | `!rank Faker KR1`              |
| `!addplayer <pseudo> <tag>` | Ajoute un joueur à la liste suivie (le pseudo doit commencer par `FIS`) | `!addplayer FIS Marmelade FIS` |

> Pour `!addplayer`, le dernier mot est le tag, tout ce qui précède est le pseudo (les espaces sont acceptés).
