# DofusSwitch

> 🇫🇷 Gestionnaire de fenêtres multi-comptes pour Dofus sous Linux (X11)
> 
> 🇬🇧 Multi-account window manager for Dofus on Linux (X11)

---

## 🇫🇷 Table des matières · 🇬🇧 Table of Contents

| 🇫🇷 Français | 🇬🇧 English |
|---|---|
| [Présentation](#présentation--overview) | [Overview](#présentation--overview) |
| [Prérequis](#prérequis--prerequisites) | [Prerequisites](#prérequis--prerequisites) |
| [Installation](#installation) | [Installation](#installation) |
| [Désinstallation](#désinstallation--uninstall) | [Uninstall](#désinstallation--uninstall) |
| [Lancement](#lancement--launching) | [Launching](#lancement--launching) |
| [Interface](#interface) | [Interface](#interface) |
| [Raccourcis](#raccourcis--shortcuts) | [Shortcuts](#raccourcis--shortcuts) |
| [Groupes A et B](#groupes-a-et-b--groups-a--b) | [Groups A & B](#groupes-a-et-b--groups-a--b) |
| [Ordre de cycle](#ordre-de-cycle--cycle-order) | [Cycle Order](#ordre-de-cycle--cycle-order) |
| [Fermer des fenêtres](#fermer-des-fenêtres--closing-windows) | [Closing Windows](#fermer-des-fenêtres--closing-windows) |
| [Fichier de configuration](#fichier-de-configuration--config-file) | [Config File](#fichier-de-configuration--config-file) |
| [Architecture du code](#architecture-du-code--code-architecture) | [Code Architecture](#architecture-du-code--code-architecture) |
| [Dépannage](#dépannage--troubleshooting) | [Troubleshooting](#dépannage--troubleshooting) |

---

## Présentation · Overview

### 🇫🇷

**DofusSwitch** est un utilitaire de bureau Linux permettant de gérer et basculer rapidement entre plusieurs fenêtres Dofus ouvertes en même temps. Il permet de :

- Détecter automatiquement les fenêtres Dofus ouvertes via `wmctrl`
- Définir des **raccourcis clavier globaux** actifs même quand DofusSwitch est en arrière-plan
- Organiser ses comptes en **groupes A et B** pour gérer plusieurs équipes
- Naviguer avec des macros **suivant / précédent** selon un ordre personnalisé
- **Fermer individuellement ou en masse** les fenêtres Dofus

### 🇬🇧

**DofusSwitch** is a Linux desktop utility to manage and switch between multiple Dofus windows simultaneously. It provides:

- Automatic detection of open Dofus windows via `wmctrl`
- **Global hotkeys** that work even when DofusSwitch is in the background
- A **group system** (A / B) to organise accounts into teams
- **Next / Previous cycle macros** to navigate windows in a defined order
- **Individual or bulk window closing**

---

## Prérequis · Prerequisites

### 🇫🇷 Configuration système requise · 🇬🇧 System requirements

| Prérequis / Requirement | Version | 🇫🇷 Remarque | 🇬🇧 Notes |
|---|---|---|---|
| Linux | Any | Session X11 obligatoire (pas Wayland) | X11 session required (not Wayland) |
| Python | 3.10+ | Vérifier avec `python3 --version` | Check with `python3 --version` |
| pip | Any | Généralement inclus avec Python | Usually bundled with Python |
| wmctrl | Any | Outil de gestion des fenêtres X11 | Window management via CLI |
| xdotool | Any | Optionnel — améliore la détection AppImage | Optional — improves AppImage detection |

> 🇫🇷 **Note Wayland :** DofusSwitch utilise `wmctrl` qui nécessite une session X11. Sous GNOME avec Wayland, choisissez une session Xorg depuis l'écran de connexion, ou forcez X11 avec `XDG_SESSION_TYPE=x11`.
>
> 🇬🇧 **Wayland note:** DofusSwitch relies on `wmctrl` which requires an X11 session. On GNOME with Wayland, switch to an Xorg session from the login screen, or force X11 with `XDG_SESSION_TYPE=x11`.

### 🇫🇷 Paquets Python requis · 🇬🇧 Python packages

| Paquet / Package | Version | 🇫🇷 Rôle | 🇬🇧 Role |
|---|---|---|---|
| PyQt6 | 6.x | Interface graphique | GUI framework |
| pynput | 1.7+ | Capture des raccourcis globaux | Global hotkey capture |

### 🇫🇷 Installer les dépendances système · 🇬🇧 Installing system dependencies

**Debian / Ubuntu / Linux Mint:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv wmctrl xdotool
```

**Arch Linux / Manjaro:**
```bash
sudo pacman -S python python-pip wmctrl xdotool
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip wmctrl xdotool
```

### 🇫🇷 Paquets Python manuellement · 🇬🇧 Python packages manually

```bash
pip install PyQt6 pynput
```

> 🇫🇷 Il est recommandé d'utiliser un environnement virtuel pour éviter les conflits :
>
> 🇬🇧 It is recommended to use a virtual environment to avoid conflicts:
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install PyQt6 pynput
> python main.py
> ```

---

## Installation

### 🇫🇷

Placez `main.py`, `install.sh` et `uninstall.sh` dans le même dossier, puis exécutez :

### 🇬🇧

Place `main.py`, `install.sh` and `uninstall.sh` in the same folder, then run:

```bash
chmod +x install.sh
./install.sh
```

| # | 🇫🇷 | 🇬🇧 |
|---|---|---|
| 1 | Copie `main.py` dans `~/.local/share/dofusswitch/` | Copy `main.py` to `~/.local/share/dofusswitch/` |
| 2 | Crée un environnement virtuel dédié avec PyQt6 et pynput | Create a dedicated virtualenv with PyQt6 and pynput |
| 3 | Installe `wmctrl` automatiquement via `apt` si absent | Install `wmctrl` automatically if missing (via `apt`) |
| 4 | Crée un script de lancement dans `~/.local/bin/dofusswitch` | Create a launcher at `~/.local/bin/dofusswitch` |
| 5 | Crée un fichier `.desktop` pour le menu des applications | Create a `.desktop` entry for your application menu |
| 6 | Génère une icône SVG si aucun `icon.png` n'est présent | Generate an SVG icon if no `icon.png` is found |

> 🇫🇷 Si `~/.local/bin` n'est pas dans votre `$PATH`, ajoutez à votre `~/.bashrc` ou `~/.zshrc` :
>
> 🇬🇧 If `~/.local/bin` is not in your `$PATH`, add to your `~/.bashrc` or `~/.zshrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
> 🇫🇷 Puis rechargez : `source ~/.bashrc` · 🇬🇧 Then reload: `source ~/.bashrc`

---

## Désinstallation · Uninstall

```bash
./uninstall.sh
```

🇫🇷 Le script demande si vous souhaitez également supprimer la configuration dans `~/.config/dofusswitch/`.

🇬🇧 The script will ask whether to also delete the configuration at `~/.config/dofusswitch/`.

---

## Lancement · Launching

🇫🇷 **Depuis le terminal :** · 🇬🇧 **From the terminal:**
```bash
dofusswitch
```

🇫🇷 **Depuis le menu des applications :** Recherchez **DofusSwitch** dans votre lanceur (Activités GNOME, Kickoff KDE, Whisker XFCE…).

🇬🇧 **From the application menu:** Search for **DofusSwitch** in your launcher (GNOME Activities, KDE Kickoff, XFCE Whisker…).

---

## Interface

### 🇫🇷 En-tête · 🇬🇧 Header

| Élément / Element | 🇫🇷 Description | 🇬🇧 Description |
|---|---|---|
| FENETRES | Nombre total de fenêtres détectées | Total number of detected windows |
| GROUPE A | Nombre de comptes du groupe A | Number of accounts in group A |
| GROUPE B | Nombre de comptes du groupe B | Number of accounts in group B |
| Pastille / Status pill | Nombre de raccourcis actifs | Active shortcut count |

### 🇫🇷 Macros globales · 🇬🇧 Global Macros

| Carte / Card | 🇫🇷 ▶ Suivant | 🇬🇧 ▶ Next | 🇫🇷 ◀ Précédent | 🇬🇧 ◀ Previous |
|---|---|---|---|---|
| Cycle total | Fenêtre suivante (tous groupes) | Next window (all groups) | Fenêtre précédente | Previous window |
| Cycle groupe A | Suivant dans le groupe A | Next in group A | Précédent dans le groupe A | Previous in group A |
| Cycle groupe B | Suivant dans le groupe B | Next in group B | Précédent dans le groupe B | Previous in group B |

🇫🇷 Pour assigner un raccourci : **cliquer sur le champ**, puis **appuyer sur la combinaison souhaitée**. `Échap` pour effacer.

🇬🇧 To assign a shortcut: **click the field**, then **press the desired key combination**. `Escape` to clear.

### 🇫🇷 Comptes détectés · 🇬🇧 Detected Accounts

| Colonne / Column | 🇫🇷 Description | 🇬🇧 Description |
|---|---|---|
| ▲ / # / ▼ | Position dans l'ordre de cycle | Cycle order position |
| PID | Identifiant système du processus | System process identifier |
| ✕ Fermer | Ferme cette fenêtre | Close this window |
| Nom / Name | Nom du compte (modifiable) | Editable account name |
| Groupe A/B | Cliquer pour basculer | Click to toggle |
| Raccourci / Shortcut | Touche de focus direct | Direct focus hotkey |
| 👁 | Amène la fenêtre au premier plan | Bring window to front |
| Focus | Bascule vers cette fenêtre | Switch to this window |

### 🇫🇷 Pied de page · 🇬🇧 Footer

| Bouton / Button | 🇫🇷 Action | 🇬🇧 Action |
|---|---|---|
| ↺ Actualiser | Rescanne les fenêtres Dofus | Rescan for open Dofus windows |
| ✓ Sauvegarder | Sauvegarde manuelle | Manual save |

🇫🇷 La configuration est également sauvegardée automatiquement à chaque modification.

🇬🇧 Configuration is also saved automatically on every change.

---

## Raccourcis · Shortcuts

### 🇫🇷 Raccourci individuel par compte · 🇬🇧 Per-account shortcut

🇫🇷 Chaque compte peut avoir sa propre touche de focus direct. Cliquez sur **"Configurer une macro"** dans la ligne du compte, puis appuyez sur la combinaison souhaitée. Ce raccourci est **global** : il fonctionne même quand DofusSwitch est en arrière-plan.

🇬🇧 Each account can have its own direct focus key. Click the **"Configurer une macro"** field and press the desired combination. This shortcut is **global** — it works even when DofusSwitch is minimised.

🇫🇷 **Combinaisons supportées :** `Ctrl`, `Alt`, `Shift` + `F1`–`F12`, lettres, chiffres, `Espace`. `Échap` pour effacer.

🇬🇧 **Supported combinations:** `Ctrl`, `Alt`, `Shift` + `F1`–`F12`, letters, digits, `Space`. `Escape` to clear.

### 🇫🇷 Macros de cycle · 🇬🇧 Cycle macros

🇫🇷 Les macros de cycle permettent de naviguer entre les fenêtres sans connaître les raccourcis individuels. Le cycle est **bouclant** : après la dernière fenêtre, il revient à la première.

🇬🇧 Cycle macros let you navigate accounts without knowing individual shortcuts. The cycle **wraps around**: after the last window it returns to the first.

---

## Groupes A et B · Groups A & B

🇫🇷 Les groupes permettent de séparer les comptes en deux équipes indépendantes. Cliquez sur le badge **Groupe A** ou **Groupe B** d'un compte pour le basculer. Les statistiques de l'en-tête se mettent à jour en temps réel.

🇬🇧 Groups allow you to split accounts into two independent teams. Click the **Groupe A** / **Groupe B** badge on any row to toggle it. Header stats update in real time.

**🇫🇷 Exemple · 🇬🇧 Example:**
```
🇫🇷  Groupe A → Tank, Heal, Support    (Cycle groupe A pour l'équipe de combat)
     Groupe B → Craft, Récolte         (Cycle groupe B pour les métiers)

🇬🇧  Group A  → Tank, Healer, Support  (Cycle groupe A during combat)
     Group B  → Crafter, Harvester     (Cycle groupe B for professions)
```

---

## Ordre de cycle · Cycle Order

🇫🇷 Chaque compte possède un numéro d'ordre (1–99) affiché dans le bloc ▲/▼. Les fenêtres sont parcourues du **numéro le plus bas au plus haut**. L'ordre est indépendant par groupe et pour le cycle total.

🇬🇧 Each account has an order number (1–99) shown in the ▲/▼ block. Windows are cycled **lowest number first**. Order is independent per group and for the total cycle.

---

## Fermer des fenêtres · Closing Windows

| 🇫🇷 Action | 🇬🇧 Action | 🇫🇷 Comment | 🇬🇧 How |
|---|---|---|---|
| Fermer une fenêtre | Close one window | Bouton **✕ Fermer** sous le PID | **✕ Fermer** button below the PID |
| Fermer toutes | Close all windows | Bouton **✕ Fermer tous les comptes** | **✕ Fermer tous les comptes** button |

🇫🇷 Une **boîte de confirmation** s'affiche avant la fermeture groupée pour éviter les accidents.

🇬🇧 A **confirmation dialog** appears before bulk closing to prevent accidents.

---

## Fichier de configuration · Config File

🇫🇷 La configuration est stockée dans · 🇬🇧 Configuration is stored at:

```
~/.config/dofusswitch/config.json
```

**🇫🇷 Exemple de structure · 🇬🇧 Example structure:**

```json
{
    "global": {
        "cycle_hk":        "f1",
        "cycle_prev_hk":   "f2",
        "group_a_hk":      "f3",
        "group_a_prev_hk": "f4",
        "group_b_hk":      "f5",
        "group_b_prev_hk": "f6"
    },
    "12345": {
        "order": 1,
        "name":  "Roublard",
        "hk":    "<alt>+1",
        "group": "A"
    }
}
```

| Clé / Key | Type | 🇫🇷 Description | 🇬🇧 Description |
|---|---|---|---|
| `global.cycle_hk` | string | Cycle total — suivant | Total cycle — next |
| `global.cycle_prev_hk` | string | Cycle total — précédent | Total cycle — previous |
| `global.group_a_hk` | string | Cycle groupe A — suivant | Group A cycle — next |
| `global.group_a_prev_hk` | string | Cycle groupe A — précédent | Group A cycle — previous |
| `global.group_b_hk` | string | Cycle groupe B — suivant | Group B cycle — next |
| `global.group_b_prev_hk` | string | Cycle groupe B — précédent | Group B cycle — previous |
| `[PID].order` | int | Position dans l'ordre de cycle | Position in cycle order |
| `[PID].name` | string | Nom affiché du compte | Display name |
| `[PID].hk` | string | Raccourci de focus direct | Direct focus shortcut |
| `[PID].group` | `"A"` / `"B"` | Groupe d'appartenance | Group membership |

🇫🇷 Réinitialiser la configuration · 🇬🇧 Reset configuration:
```bash
rm ~/.config/dofusswitch/config.json
```

---

## Architecture du code · Code Architecture

```
main.py
│
├── 🇫🇷 Fonctions utilitaires · 🇬🇧 Config helpers
│   ├── load_config()          🇫🇷 Lecture JSON · 🇬🇧 Read JSON config
│   └── save_config()          🇫🇷 Écriture JSON · 🇬🇧 Write JSON config
│
├── 🇫🇷 Fonctions système X11 · 🇬🇧 X11 helpers
│   ├── get_dofus_windows()    🇫🇷 Détection via wmctrl · 🇬🇧 Detect via wmctrl
│   ├── focus_window(wid)      wmctrl -i -a
│   └── close_window(wid)      wmctrl -i -c
│
├── 🇫🇷 Widgets PyQt6 · 🇬🇧 Widgets
│   ├── HotkeyLineEdit         🇫🇷 Champ de saisie de touche · 🇬🇧 Key capture field
│   ├── GroupBadge             🇫🇷 Bouton toggle A ↔ B · 🇬🇧 Toggle button A ↔ B
│   ├── MacroCard              🇫🇷 Carte macro suivant/précédent · 🇬🇧 Next/prev macro card
│   └── AccountRow             🇫🇷 Ligne de compte complète · 🇬🇧 Full account row
│
└── DofusSwitchApp  (QMainWindow)
    ├── _auto_resize()         🇫🇷 Redimensionne selon le nb de comptes · 🇬🇧 Resize by account count
    ├── _build_ui()            🇫🇷 Construit l'interface · 🇬🇧 Build the UI
    ├── refresh()              🇫🇷 Rescanne et reconstruit · 🇬🇧 Rescan and rebuild
    ├── _update_stats()        🇫🇷 Met à jour les stats · 🇬🇧 Refresh stat cards
    ├── cycle_logic()          🇫🇷 Navigation suivant/précédent · 🇬🇧 Next/previous navigation
    ├── restart_hotkeys()      🇫🇷 Recharge le mapping pynput · 🇬🇧 Rebuild pynput mapping
    ├── update_data()          🇫🇷 Persiste les modifs par compte · 🇬🇧 Persist per-account changes
    ├── update_global_hks()    🇫🇷 Persiste les macros globales · 🇬🇧 Persist global macros
    └── manual_save()          🇫🇷 Sauvegarde manuelle · 🇬🇧 Explicit save with feedback
```

### 🇫🇷 Flux des raccourcis · 🇬🇧 Hotkey flow

```
🇫🇷 Pression d'une touche · 🇬🇧 Key press
        │
        ▼
pynput.GlobalHotKeys
        │
        ├── 🇫🇷 Raccourci individuel · 🇬🇧 Individual shortcut  →  focus_window(wid)
        │
        ├── 🇫🇷 Macro suivant · 🇬🇧 Next macro      →  cycle_logic(group, direction=+1)
        │
        └── 🇫🇷 Macro précédent · 🇬🇧 Previous macro  →  cycle_logic(group, direction=-1)
                                                               │
                                                               ▼
                                     🇫🇷 Filtrer par groupe · 🇬🇧 Filter by group
                                     🇫🇷 Trier par ordre · 🇬🇧 Sort by order
                                     🇫🇷 Calculer l'index · 🇬🇧 Compute index (modulo)
                                     wmctrl -i -a [wid]
```

---

## Dépannage · Troubleshooting

### 🇫🇷 Aucune fenêtre détectée · 🇬🇧 No windows detected

```bash
# 🇫🇷 Vérifier que wmctrl est installé · 🇬🇧 Check wmctrl is installed
which wmctrl

# 🇫🇷 Vérifier que Dofus est visible · 🇬🇧 Check Dofus windows are visible
wmctrl -l | grep -i dofus
```

🇫🇷 Puis cliquez sur **Actualiser** dans l'interface.

🇬🇧 Then click **Actualiser** in the interface.

### 🇫🇷 Les raccourcis ne fonctionnent pas · 🇬🇧 Hotkeys not working

🇫🇷 Sur certaines distributions, `pynput` nécessite que l'utilisateur soit dans le groupe `input` :

🇬🇧 On some distributions, `pynput` requires the user to be in the `input` group:

```bash
sudo usermod -aG input $USER
# 🇫🇷 Se déconnecter puis se reconnecter · 🇬🇧 Log out and back in
```

### 🇫🇷 Application absente du menu · 🇬🇧 App not in application menu

```bash
update-desktop-database ~/.local/share/applications
```

### 🇫🇷 AppImage — mauvais nom de fenêtre · 🇬🇧 AppImage — wrong window name

🇫🇷 Lancez ces commandes pendant que Dofus est ouvert :

🇬🇧 Run the following while Dofus is open:

```bash
wmctrl -l -p
xdotool search --name "dofus" getwindowname %@
```

🇫🇷 Le résultat permet d'affiner la détection dans `get_dofus_windows()`.

🇬🇧 Share the output to refine the detection logic in `get_dofus_windows()`.

### 🇫🇷 Session Wayland — wmctrl ne fonctionne pas · 🇬🇧 Wayland — wmctrl not working

🇫🇷 Passez en session Xorg depuis l'écran de connexion, ou forcez X11 :

🇬🇧 Switch to an Xorg session from the login screen, or force X11:

```bash
XDG_SESSION_TYPE=x11 dofusswitch
```

---

*🇫🇷 DofusSwitch — Projet open source personnel. Non affilié à Ankama Games.*

*🇬🇧 DofusSwitch — Personal open-source project. Not affiliated with Ankama Games.*
