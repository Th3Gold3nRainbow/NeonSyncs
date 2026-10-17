# NeonSyncs — Review of Internationalization Translations (i18n)

This document lists translations in **Russian (RU)** and **Arabic (AR)** that have subtle linguistic or contextual nuances, so they can be easily reviewed or adjusted if desired.

---

## 1. Russian (Русский) Translation Review

| Key | Current Translation | Alternative Option | Linguistic Context & Notes |
|---|---|---|---|
| `back_10` / `back_30` / `fwd_10` / `fwd_30` | `⏪ 10с`, `⏪ 30с`, `10с ⏩`, `30с ⏩` | `⏪ 10 сек`, `10 сек ⏩` | `с` is the official SI abbreviation for seconds (секунда), compact on player buttons. `сек` is sometimes preferred in casual desktop UIs. |
| `label_user` | `Имя пользователя` | `Никнейм` / `Псевдоним` | `Имя пользователя` is the standard official Windows / Qt UI term. `Никнейм` is more informal / gamer-oriented. |
| `label_room` | `Комната` | `Комната` / `Зал` | `Комната` is universally accepted for virtual watchparty rooms (Syncplay, Watch2Gether, Discord). |
| `section_users` | `УЧАСТНИКИ` | `ПОЛЬЗОВАТЕЛИ` | `УЧАСТНИКИ` ("Participants") is used instead of literal "Users", which feels much more natural for a shared video playback room. |
| `p2p_error_no_turn` | `Сбой подключения (вероятно, строгий NAT без TURN)` | `Сбой подключения (вероятно, NAT без TURN)` | Mentions strict NAT and absence of TURN relay server, very precise for peer-to-peer WebRTC diagnostics. |
| `status_disconnected_lost` | `Отключено (связь потеряна)` | `Отключено (соединение разорвано)` | Both are natural; `связь потеряна` conveys sudden network packet drop well. |
| `dialog_open_video_title` | `Выберите видеофайл` | `Выбрать видео…` | `Выберите видеофайл` matches Windows file open dialog conventions. |

---

## 2. Arabic (العربية) Translation Review

| Key | Current Translation | Alternative Option | Linguistic Context & Notes |
|---|---|---|---|
| `room_id` | `معرف الغرفة` | `رمز الغرفة` / `معرّف الغرفة` | `معرف الغرفة` translates "Room ID" (Identifier). `رمز الغرفة` would mean "Room Code". `معرف الغرفة` is technically accurate for alphanumeric IDs (`neonsyncs-xxxxxx`). |
| `section_users` | `المستخدمون` | `المشاركون` | `المستخدمون` translates "USERS". `المشاركون` ("Participants") is also a very natural alternative in a watch party context. |
| `back_10` / `fwd_10` | `⏪ 10 ث`, `10 ث ⏩` | `⏪ 10 ثوانٍ`, `10 ثوانٍ ⏩` | `ث` is the standard abbreviation for ثانية (second) to prevent button labels from overflowing. Temporal direction is preserved (left = back, right = forward). |
| `status_disconnected_lost` | `انقطع الاتصال (فُقد الارتباط)` | `انقطع الاتصال (فقدان الاتصال بالخادم)` | `فُقد الارتباط` is concise and describes both P2P and server connection drop. |
| `p2p_error_signaling` | `تعذر الوصول إلى خادم الإشارات` | `فشل الاتصال بخادم الإشارات` | `تعذر الوصول إلى خادم الإشارات` is very natural for "Signaling server unreachable". |
| `p2p_error_no_turn` | `فشل الاتصال (يُحتمل وجود NAT دون خادم TURN)` | `فشل الاتصال بسبب قيود الشبكة (NAT/TURN)` | Technical explanation of symmetric NAT and missing TURN relay. |
| `warning_different_file` | `الملف يختلف عن ملف المضيف ({details}) — تم إيقاف المزامنة مؤقتاً.` | `الملف مختلف عن ملف المضيف ({details}) — تم تعليق المزامنة.` | Both are grammatically sound Modern Standard Arabic. |
| `chat_placeholder` | `اكتب رسالة…` | `اكتب رسالة هنا…` | `اكتب رسالة…` is concise and clean for the text input box. |

---

## 3. General Rules Followed

1. **Brand Name**: `NeonSyncs` is kept in Latin script without transliteration across all 4 languages.
2. **P2P Room ID Prefix**: `neonsyncs-` is kept in ASCII in all languages as it is part of the signaling protocol.
3. **Format Variables**: Variables `{id}`, `{file}`, `{details}`, `{message}`, `{error}` are placed in natural grammatical order and validated automatically by `tools/check_i18n.py`.
