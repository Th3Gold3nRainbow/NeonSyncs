# Identité Visuelle — NeonSyncs (https://neonsyncs.com)

Ce document récapitule l'ensemble des tokens visuels, polices, composants et assets extraits du code source du site officiel **NeonSyncs** (`SyncProject - Copie`). Il sert de référence unique pour le rebrand de l'application de bureau dans `Sync`.

---

## 1. Palette de Couleurs (Tokens)

### Thème par défaut (« Cyber Cyan »)

| Token | Valeur CSS / Hex / RGBA | Usage dans le site | Usage dans l'application PyQt5 (NeonSyncs) |
| :--- | :--- | :--- | :--- |
| `bg` | `#08070d` | Fond d'écran principal (noir profond bleuté/violacé) | `window_bg` : fond de la fenêtre principale |
| `bg-2` | `#0e091a` | Teinte secondaire de dégradé d'ambiance | `panel_bg` : fond des panneaux et cartes sombres |
| `surface` | `rgba(10, 7, 22, 0.75)` / `#0a0716` | Cartes en verre (`.glass`), panneau de chat | `surface_bg` : fond du chat, liste des salons |
| `surface-2` | `rgba(14, 9, 28, 0.90)` / `#0e091c` | Cartes en verre renforcé (`.glass-strong`) | `card_bg` : conteneurs de formulaire, dialogues |
| `surface-input` | `rgba(8, 8, 18, 0.80)` / `#080812` | Fond des champs de saisie (`.input-neon`) | `input_bg` : `QLineEdit`, `QTextEdit`, `QComboBox` |
| `border` | `rgba(0, 240, 255, 0.18)` / `#00f0ff2e` | Bordures standards des cartes et séparateurs | `border_default` : bordures d'éléments inactifs |
| `border-subtle` | `rgba(0, 240, 255, 0.12)` | Séparateurs, bordures secondaires | `border_subtle` : séparateur de barre d'outils |
| `border-focus` | `rgba(0, 240, 255, 0.60)` | Bordure active au focus d'un champ | `border_focus` : contour lors de la saisie active |
| `neon-primary` | `#00f0ff` | Cyan néon (accent principal, logo, titres, boutons) | `accent_primary` : boutons primaires, seek bar active |
| `neon-secondary` | `#a855f7` | Violet néon (accent secondaire, partie « SYNC ») | `accent_secondary` : badges, surbrillance secondaire |
| `neon-glow` | `rgba(0, 240, 255, 0.70)` | Halo lumineux cyan standard | `glow_primary` : lueur du lecteur / bouton actif |
| `neon-glow-secondary` | `rgba(168, 85, 247, 0.70)` | Halo lumineux violet | `glow_secondary` : lueur secondaire |
| `text` | `#eaeaf6` | Texte principal (blanc chaud très lisible) | `text_primary` : labels, texte de saisie, messages |
| `text-muted` | `#8383a6` | Texte secondaire, placeholders, timestamps | `text_muted` : placeholders, horodatages, labels discrets |
| `neon-green` | `#00ff9d` | Statut connecté, validation, succès | `status_connected` : statut P2P connecté, fichiers validés |
| `neon-green-bg` | `rgba(34, 197, 94, 0.10)` | Fond de badge succès | Fond de notification / badge succès |
| `neon-green-border`| `rgba(34, 197, 94, 0.30)` | Bordure de badge succès | Bordure statut connecté |
| `neon-red` | `#ff3860` (ou `#ef4444`) | Erreurs, bouton hôte strict, avertissements | `status_error` : erreurs de connexion, mot de passe incorrect |
| `neon-red-bg` | `rgba(239, 68, 68, 0.10)` | Fond de message d'erreur | Fond du conteneur d'erreur |
| `neon-red-border` | `rgba(239, 68, 68, 0.30)` | Bordure de message d'erreur | Bordure des alertes d'erreur |
| `neon-amber` | `#ffb627` (ou `#f59e0b`) | Reconnexion, rôle contrôleur, avertissement | `status_reconnecting` : statut de reconnexion P2P |
| `neon-amber-bg` | `rgba(245, 158, 11, 0.10)` | Fond de statut reconnexion | Fond de bannière reconnexion |
| `btn-neon-bg` | `rgba(0, 240, 255, 0.12)` -> `0.03` | Dégradé vertical du bouton néon cyan | `QPushButton` primaire |
| `btn-neon-hover-bg` | `rgba(0, 240, 255, 0.26)` -> `0.10` | Dégradé vertical au survol | `QPushButton:hover` primaire |
| `btn-pink-border` | `rgba(229, 9, 20, 0.50)` | Bouton secondaire (« Join Room » / « Host only ») | Bouton d'action secondaire |

---

## 2. Typographie

| Rôle | Police | Graisses | Source / Licence | Fallback |
| :--- | :--- | :--- | :--- | :--- |
| **Titres & Display** | **Orbitron** | 700 (Bold), 900 (Black) | Google Fonts / SIL Open Font License 1.1 | `system-ui, sans-serif` |
| **Corps & Interface** | **Rajdhani** | 500 (Medium), 600 (SemiBold), 700 (Bold) | Google Fonts / SIL Open Font License 1.1 | `Segoe UI, system-ui, sans-serif` |
| **Codes & Monospace** | **Orbitron** (ou monospace) | 700 (Bold) | Google Fonts / SIL Open Font License 1.1 | `Consolas, monospace` |

> **Note sur la licence** : Les polices **Orbitron** (par Matt McInerney) et **Rajdhani** (par Indian Type Foundry) sont distribuées sous licence libre **SIL Open Font License (OFL)**, qui autorise explicitement l'incorporation, la distribution et l'utilisation commerciale/personnelle sans royalties.

---

## 3. Rayons de Bordure et Espacements

### Rayons de bordure (`border-radius`)
- **Cartes & Conteneurs principaux** : `16px` (`rounded-2xl`)
- **Blocs internes & panneaux secondaires** : `12px` (`rounded-xl`)
- **Champs de saisie & Boutons** : `8px` (`rounded-lg`)
- **Badges, Pilules, Pastilles de statut & Curseur de scrollbar** : `999px` (`rounded-full`)

### Espacements (`padding` & `margin`)
- **Cartes de groupe** : `16px` à `24px`
- **Champs de saisie** : `10px 14px`
- **Boutons standard** : `10px 16px`
- **Boutons compacts** : `6px 12px`
- **Épaisseur de scrollbar** : `6px` avec rail transparent et pouce néon `rgba(0, 240, 255, 0.25)` (`0.45` au survol)

---

## 4. Effets Néon et Luminescence

### Halos (`glow` & `box-shadow`)
- **Bordure lumineuse cyan standard** : `0 0 0 1px #00f0ff, 0 0 18px rgba(0, 240, 255, 0.70)`
- **Bordure lumineuse violette standard** : `0 0 0 1px #a855f7, 0 0 18px rgba(168, 85, 247, 0.70)`
- **Lueur au focus d'un champ** : `0 0 16px rgba(0, 240, 255, 0.22)`
- **Lueur survol bouton néon** : `0 0 35px rgba(0, 240, 255, 0.75), 0 0 70px rgba(0, 240, 255, 0.40)`
- **Lueur texte néon (`text-shadow`)** : `0 0 8px rgba(0, 240, 255, 0.70), 0 0 20px rgba(0, 240, 255, 0.70)`

### Dégradés
- **Fond de fenêtre** :
  `radial-gradient(ellipse 140% 120% at 80% 110%, rgba(168, 85, 247, 0.08) 0%, #0e091a 45%, #08070d 100%)`
- **Bouton néon primaire** :
  `linear-gradient(180deg, rgba(0, 240, 255, 0.12), rgba(0, 240, 255, 0.03))`
- **Bouton néon survol** :
  `linear-gradient(180deg, rgba(0, 240, 255, 0.26), rgba(0, 240, 255, 0.10))`
- **Titre / Gradient icône** :
  `linear-gradient(135deg, #22d3ee 0%, #ec4899 100%)` (Cyan vers Rose/Fuchsia)

---

## 5. Assets et Logos copiés dans `brand/`

1. **[`brand/favicon.svg`](file:///C:/Users/Twix/Desktop/Sync/brand/favicon.svg)** : Favicon officiel du site (carré sombre arrondi `rx=14`, bordure cyan 0.4, perforations de film 35mm, play triangulaire dégradé cyan vers rose avec halo néon).
2. **[`brand/logo-reel.svg`](file:///C:/Users/Twix/Desktop/Sync/brand/logo-reel.svg)** : Logo vectoriel complet issu du composant `NeonSyncLogo.tsx` (bobine de film avec perforations, rayons, moyeu central et arcs de synchronisation rayonnants).
3. **[`brand/logo-play.svg`](file:///C:/Users/Twix/Desktop/Sync/brand/logo-play.svg)** : Logo épuré issu du composant `Lobby.tsx` (cercle néon avec triangle play néon et halo de lueur).
4. **[`brand/image.png`](file:///C:/Users/Twix/Desktop/Sync/brand/image.png)** : Asset PNG du site (185x39).
5. **[`brand/og-image.png`](file:///C:/Users/Twix/Desktop/Sync/brand/og-image.png)** : Image OpenGraph officielle (1200x630).

---

## 6. Éléments Manquants sur le Site

Certaines ressources nécessaires à une application desktop Windows ne sont pas présentes sur le site web et doivent être créées ou approvisionnées :

1. **Fichiers de polices `.ttf` / `.woff2` embarqués** :
   - *État sur le site* : Les familles `'Orbitron'` et `'Rajdhani'` sont référencées dans le CSS sans balise `<link>` Google Fonts ni fichiers locaux dans `public/`.
   - *Solution pour l'app* : Télécharger les versions TTF officielles sous licence libre SIL OFL et les placer dans `assets/fonts/` pour un rendu identique sur tous les PC Windows sans dépendance internet.
2. **Fichier `icon.ico` multi-résolution pour Windows** :
   - *État sur le site* : Seul `favicon.svg` est présent.
   - *Solution pour l'app* : À générer en Phase 2 avec résolutions 16, 24, 32, 48, 64, 128, 256 px avec fond transparent à partir du logo officiel.
3. **Images de l'installateur Inno Setup (`wizard-image.bmp` et `wizard-small-image.bmp`)** :
   - *État sur le site* : Inexistant (spécifique aux installateurs Windows).
   - *Solution pour l'app* : À générer en Phase 2 aux résolutions 164x314 et 55x58 aux couleurs du site (fond sombre `#08070d`, logo néon et dégradé cyan/violet).
