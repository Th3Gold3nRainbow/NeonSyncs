#!/usr/bin/env python3
"""
assets/make_logo.py
===================
Script reproductible qui génère l'ensemble des assets graphiques de NeonSyncs
à partir du logo vectoriel officiel dans brand/ :
  - icon.ico (multi-résolution : 16, 24, 32, 48, 64, 128, 256 px, fond transparent)
  - wizard-image.bmp (164x314 px, 24-bit RGB) pour le volet gauche de l'installateur Inno Setup
  - wizard-small-image.bmp (55x58 px, 24-bit RGB) pour l'en-tête de l'installateur Inno Setup

Usage :
  python assets/make_logo.py
  (ou via venv\\Scripts\\python.exe assets/make_logo.py)
"""
import os
import sys
import struct
import shutil

from PyQt5.QtWidgets import QApplication
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import (
    QImage, QPainter, QColor, QFont, QLinearGradient, QRadialGradient,
    QFontDatabase, QPen
)
from PyQt5.QtCore import Qt, QRectF, QPointF, QByteArray, QBuffer, QIODevice


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_DIR = os.path.join(BASE_DIR, "brand")
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")


def load_fonts():
    if os.path.isdir(FONTS_DIR):
        for f in os.listdir(FONTS_DIR):
            if f.lower().endswith((".ttf", ".otf")):
                QFontDatabase.addApplicationFont(os.path.join(FONTS_DIR, f))


def build_ico(svg_path, out_ico_path, sizes=(16, 24, 32, 48, 64, 128, 256)):
    """Génère un fichier .ico multi-résolution avec fond transparent à partir d'un SVG."""
    renderer = QSvgRenderer(svg_path)
    images_data = []

    for s in sizes:
        img = QImage(s, s, QImage.Format_ARGB32_Premultiplied)
        img.fill(QColor(0, 0, 0, 0))
        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()

        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.WriteOnly)
        img.save(buf, "PNG")
        images_data.append((s, bytes(ba)))

    count = len(images_data)
    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count
    entries = []
    data_blobs = []

    for s, data in images_data:
        w = s if s < 256 else 0
        h = s if s < 256 else 0
        size = len(data)
        entry = struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, size, offset)
        entries.append(entry)
        data_blobs.append(data)
        offset += size

    with open(out_ico_path, "wb") as f:
        f.write(header)
        for e in entries:
            f.write(e)
        for d in data_blobs:
            f.write(d)

    print(f"  -> {out_ico_path} ({count} tailles : {', '.join(str(s) for s in sizes)})")


def build_wizard_image(svg_path, out_bmp_path):
    """Génère wizard-image.bmp (164x314 px, RGB 24bpp) aux couleurs de neonsyncs.com."""
    w_img = QImage(164, 314, QImage.Format_RGB888)
    p = QPainter(w_img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.setRenderHint(QPainter.SmoothPixmapTransform)

    # Dégradé de fond sombre officiel (#08070d -> #0e091a)
    bg_grad = QLinearGradient(0, 0, 0, 314)
    bg_grad.setColorAt(0.0, QColor("#08070d"))
    bg_grad.setColorAt(0.5, QColor("#0c0916"))
    bg_grad.setColorAt(1.0, QColor("#0e091a"))
    p.fillRect(0, 0, 164, 314, bg_grad)

    # Halos néon d'ambiance
    glow_cyan = QRadialGradient(82, 75, 75)
    glow_cyan.setColorAt(0.0, QColor(0, 240, 255, 40))
    glow_cyan.setColorAt(1.0, QColor(0, 240, 255, 0))
    p.fillRect(0, 0, 164, 150, glow_cyan)

    glow_pink = QRadialGradient(82, 230, 80)
    glow_pink.setColorAt(0.0, QColor(168, 85, 247, 30))
    glow_pink.setColorAt(1.0, QColor(168, 85, 247, 0))
    p.fillRect(0, 150, 164, 164, glow_pink)

    # Logo officiel centré
    renderer = QSvgRenderer(svg_path)
    logo_rect = QRectF((164 - 68) / 2, 28, 68, 68)
    renderer.render(p, logo_rect)

    # Titre officiel : NEON en cyan, SYNCS en violet
    f_title = QFont("Orbitron", 14, QFont.Bold)
    f_title.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
    p.setFont(f_title)
    p.setPen(QColor("#00f0ff"))
    p.drawText(QRectF(0, 108, 164, 25), Qt.AlignCenter, "NEON")

    p.setPen(QColor("#a855f7"))
    p.drawText(QRectF(0, 130, 164, 25), Qt.AlignCenter, "SYNCS")

    # Sous-titre
    f_sub = QFont("Rajdhani", 8, QFont.Bold)
    f_sub.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    p.setFont(f_sub)
    p.setPen(QColor("#8383a6"))
    p.drawText(QRectF(0, 160, 164, 18), Qt.AlignCenter, "WATCH IN SYNC")

    # Ligne d'accent dégradée
    line_grad = QLinearGradient(32, 184, 132, 184)
    line_grad.setColorAt(0.0, QColor(0, 240, 255, 0))
    line_grad.setColorAt(0.5, QColor(0, 240, 255, 180))
    line_grad.setColorAt(1.0, QColor(168, 85, 247, 0))
    pen = QPen(line_grad, 1.5)
    p.setPen(pen)
    p.drawLine(QPointF(32, 184), QPointF(132, 184))

    # Points clés
    f_bullet = QFont("Rajdhani", 8, QFont.DemiBold)
    p.setFont(f_bullet)
    bullets = [
        ("P2P Direct Sync", "#eaeaf6"),
        ("100% Client-Side", "#00ff9d"),
        ("No Account Required", "#8383a6"),
    ]
    y_b = 204
    for text, color in bullets:
        p.setPen(QColor(color))
        p.drawText(QRectF(16, y_b, 132, 18), Qt.AlignCenter, text)
        y_b += 22

    # Lien site web
    f_url = QFont("Orbitron", 6, QFont.Bold)
    f_url.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
    p.setFont(f_url)
    p.setPen(QColor(0, 240, 255, 160))
    p.drawText(QRectF(0, 288, 164, 18), Qt.AlignCenter, "NEONSYNCS.COM")

    p.end()
    w_img.save(out_bmp_path, "BMP")
    print(f"  -> {out_bmp_path} (164x314 px)")


def build_wizard_small_image(svg_path, out_bmp_path):
    """Génère wizard-small-image.bmp (55x58 px, RGB 24bpp) pour l'en-tête de l'installateur."""
    s_img = QImage(55, 58, QImage.Format_RGB888)
    sp = QPainter(s_img)
    sp.setRenderHint(QPainter.Antialiasing)
    sp.setRenderHint(QPainter.SmoothPixmapTransform)
    sp.fillRect(0, 0, 55, 58, QColor("#08070d"))

    renderer = QSvgRenderer(svg_path)
    renderer.render(sp, QRectF((55 - 46) / 2, (58 - 46) / 2, 46, 46))
    sp.end()

    s_img.save(out_bmp_path, "BMP")
    print(f"  -> {out_bmp_path} (55x58 px)")


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    load_fonts()

    favicon_svg = os.path.join(BRAND_DIR, "favicon.svg")
    if not os.path.exists(favicon_svg):
        print(f"ERREUR : {favicon_svg} introuvable.")
        sys.exit(1)

    print("Génération des icônes et visuels NeonSyncs...")

    # 1. icon.ico (racine et dist/ si présent)
    root_ico = os.path.join(BASE_DIR, "icon.ico")
    build_ico(favicon_svg, root_ico)

    dist_dir = os.path.join(BASE_DIR, "dist")
    if os.path.isdir(dist_dir):
        dist_ico = os.path.join(dist_dir, "icon.ico")
        shutil.copyfile(root_ico, dist_ico)
        print(f"  -> {dist_ico} (copie synchronisée)")

    # 2. wizard-image.bmp (164x314 px)
    root_wiz = os.path.join(BASE_DIR, "wizard-image.bmp")
    build_wizard_image(favicon_svg, root_wiz)

    # 3. wizard-small-image.bmp (55x58 px)
    root_wiz_small = os.path.join(BASE_DIR, "wizard-small-image.bmp")
    build_wizard_small_image(favicon_svg, root_wiz_small)

    print("Tous les visuels ont été générés avec succès.")


if __name__ == "__main__":
    main()
