# Créer l'installeur Windows (.exe) de SyncMPV

Ce dossier contient tout le nécessaire pour transformer `client.py` en
un vrai installeur Windows double-cliquable. **Ces scripts doivent être
exécutés sur une machine Windows** (PyInstaller ne fait pas de
compilation croisée depuis Linux/Mac).

## Étapes

### 1. Récupérer libmpv pour Windows

`python-mpv` a besoin de la DLL native `libmpv`. Téléchargez-la ici :
https://github.com/shinchiro/mpv-winbuild-cmake/releases

Prenez une archive `mpv-dev-x86_64-...7z` (ou `mpv-x86_64-...7z`),
extrayez-en `libmpv-2.dll`, et **placez-la dans ce dossier en la
renommant `mpv-2.dll`** (ou `mpv-1.dll` selon la version de
`python-mpv` installée — le message d'erreur au lancement vous dira
laquelle il cherche si besoin d'ajuster).

### 2. Compiler le .exe

Double-cliquez sur `build_exe.bat` (ou lancez-le depuis un terminal).
Il va :
- créer un environnement virtuel Python,
- installer les dépendances (`PyQt5`, `python-mpv`, `pyinstaller`),
- produire `dist\SyncMPV.exe`, un exécutable autonome (la DLL mpv est
  embarquée dedans).

Vous pouvez déjà distribuer `dist\SyncMPV.exe` tel quel — ça fonctionne
sans installation, en portable.

### 3. (Optionnel mais recommandé) Générer un vrai installeur

Pour un installeur avec raccourcis Bureau/menu Démarrer et
désinstallation propre via le Panneau de configuration :

1. Installez **Inno Setup** : https://jrsoftware.org/isdl.php
2. Vérifiez que `icon.ico`, `wizard-image.bmp` et `wizard-small-image.bmp`
   (fournis avec le projet — logo moderne généré pour SyncMPV) sont bien
   dans le même dossier que `installer.iss`.
3. Lancez `build_installer.bat`, ou ouvrez `installer.iss` directement
   dans Inno Setup Compiler et faites *Build > Compile*.
4. Résultat : `Output\SyncMPV-Setup.exe` — c'est le fichier à
   distribuer à vos utilisateurs.

L'installeur affiche désormais un logo (icône + bandeau latéral) et
propose un choix de langue **Anglais / Français** dès son lancement,
avant même l'écran de bienvenue.

## Résumé du flux

```
client.py  --(PyInstaller, build_exe.bat)-->  dist\SyncMPV.exe
dist\SyncMPV.exe  --(Inno Setup, build_installer.bat)-->  Output\SyncMPV-Setup.exe
```

## Le serveur (`server.py`) reste à part

`server.py` n'a pas besoin d'être packagé en `.exe` — c'est généralement
un composant qu'on héberge sur un serveur/VPS ou qu'on lance en tâche
de fond sur une machine toujours allumée. Si vous voulez aussi un
`.exe` pour le serveur (ex: pour qu'un utilisateur non-technique puisse
l'héberger), le même `build_exe.bat` fonctionne en remplaçant
`client.py` par `server.py` (sans le `--windowed` ni la DLL mpv, qui ne
sont pas nécessaires côté serveur).
