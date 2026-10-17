#!/usr/bin/env python3
"""
Generate high-quality 24-bit BMP wizard images for Inno Setup:
- wizard-image.bmp: 164x314 px
- wizard-small-image.bmp: 55x55 px
"""
import os
import sys
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import (
    QGuiApplication, QImage, QPainter, QColor, QLinearGradient,
    QRadialGradient, QPen, QBrush, QFont, QPainterPath, QFontDatabase
)

def create_wizard_images():
    app = QGuiApplication(sys.argv)
    
    # Load brand fonts if available
    font_orbitron = "Segoe UI"
    font_rajdhani = "Segoe UI"
    if os.path.exists("assets/fonts/Orbitron-Bold.ttf"):
        id1 = QFontDatabase.addApplicationFont("assets/fonts/Orbitron-Bold.ttf")
        fams = QFontDatabase.applicationFontFamilies(id1)
        if fams:
            font_orbitron = fams[0]
    if os.path.exists("assets/fonts/Rajdhani-Medium.ttf"):
        id2 = QFontDatabase.addApplicationFont("assets/fonts/Rajdhani-Medium.ttf")
        fams = QFontDatabase.applicationFontFamilies(id2)
        if fams:
            font_rajdhani = fams[0]

    # 1. wizard-image.bmp: 164x314 px
    w, h = 164, 314
    img1 = QImage(w, h, QImage.Format_RGB888)
    img1.fill(QColor(5, 5, 10))
    
    p = QPainter(img1)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    p.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # Background gradient
    grad = QLinearGradient(0, 0, w, h)
    grad.setColorAt(0.0, QColor(8, 7, 16))
    grad.setColorAt(0.5, QColor(14, 11, 28))
    grad.setColorAt(1.0, QColor(5, 5, 11))
    p.fillRect(0, 0, w, h, grad)

    # Ambient neon glows (radial)
    # Violet glow top-center
    glow1 = QRadialGradient(w / 2, 70, 90)
    glow1.setColorAt(0.0, QColor(157, 0, 255, 60))
    glow1.setColorAt(0.7, QColor(157, 0, 255, 15))
    glow1.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.fillRect(0, 0, w, 160, glow1)

    # Red/Pink glow bottom-center
    glow2 = QRadialGradient(w / 2, 230, 80)
    glow2.setColorAt(0.0, QColor(229, 9, 20, 45))
    glow2.setColorAt(0.8, QColor(229, 9, 20, 10))
    glow2.setColorAt(1.0, QColor(0, 0, 0, 0))
    p.fillRect(0, 150, w, 164, glow2)

    # Subtle neon side lines
    p.setPen(QPen(QColor(0, 245, 255, 40), 1))
    p.drawLine(10, 0, 10, h)
    p.setPen(QPen(QColor(157, 0, 255, 40), 1))
    p.drawLine(w - 11, 0, w - 11, h)

    # Neon Logo (Film Reel + Triangle)
    cx, cy = w / 2, 85
    radius = 38

    # Outer neon ring (Red/Pink #E50914 / #FF2D55)
    for spread, alpha in [(6, 15), (4, 35), (2, 70), (0, 255)]:
        p.setPen(QPen(QColor(229, 9, 20, alpha), 2.5 + spread))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), radius, radius)

    # Inner dark disk
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(10, 8, 20))
    p.drawEllipse(QPointF(cx, cy), radius - 2, radius - 2)

    # Film reel notches / dots (Cyan #00F5FF & Violet #9D00FF)
    import math
    for i in range(6):
        angle = i * (2 * math.pi / 6)
        nx = cx + (radius - 12) * math.cos(angle)
        ny = cy + (radius - 12) * math.sin(angle)
        col = QColor(0, 245, 255) if i % 2 == 0 else QColor(157, 0, 255)
        p.setBrush(col)
        p.drawEllipse(QPointF(nx, ny), 3, 3)

    # Center Play Triangle (Cyan with neon glow)
    tri_path = QPainterPath()
    tri_r = 13
    tri_path.moveTo(cx - tri_r * 0.6, cy - tri_r)
    tri_path.lineTo(cx + tri_r, cy)
    tri_path.lineTo(cx - tri_r * 0.6, cy + tri_r)
    tri_path.closeSubpath()

    p.setPen(QPen(QColor(0, 245, 255, 180), 2))
    p.setBrush(QColor(0, 245, 255))
    p.drawPath(tri_path)

    # Brand Title: NeonSyncs
    p.setPen(QColor(255, 255, 255))
    f_title = QFont(font_orbitron, 13, QFont.Bold)
    f_title.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
    p.setFont(f_title)
    p.drawText(QRectF(0, 142, w, 28), Qt.AlignCenter, "NeonSyncs")

    # Tagline
    p.setPen(QColor(0, 245, 255))
    f_sub = QFont(font_rajdhani, 9, QFont.DemiBold)
    f_sub.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
    p.setFont(f_sub)
    p.drawText(QRectF(0, 168, w, 20), Qt.AlignCenter, "SYNC WATCHPARTY")

    # Decorative separator
    p.setPen(QPen(QColor(157, 0, 255, 120), 1))
    p.drawLine(35, 198, w - 35, 198)

    # Features list (Icons/text)
    f_feat = QFont(font_rajdhani, 9, QFont.Normal)
    p.setFont(f_feat)
    p.setPen(QColor(180, 180, 205))
    p.drawText(QRectF(15, 212, w - 30, 18), Qt.AlignCenter, "• Ultra-Low Latency •")
    p.drawText(QRectF(15, 230, w - 30, 18), Qt.AlignCenter, "• P2P & Server Sync •")
    p.drawText(QRectF(15, 248, w - 30, 18), Qt.AlignCenter, "• libmpv Native Power •")

    # Watermark at bottom
    p.setPen(QColor(90, 85, 120))
    f_url = QFont(font_orbitron, 7, QFont.Normal)
    f_url.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
    p.setFont(f_url)
    p.drawText(QRectF(0, 286, w, 18), Qt.AlignCenter, "neonsyncs.com")

    p.end()

    # Save wizard-image.bmp as 24-bit RGB888
    img1.save("wizard-image.bmp", "BMP")
    print("Saved wizard-image.bmp: 164x314 (24 bpp)")

    # 2. wizard-small-image.bmp: 55x55 px
    sw, sh = 55, 55
    img2 = QImage(sw, sh, QImage.Format_RGB888)
    img2.fill(QColor(8, 7, 16))

    p2 = QPainter(img2)
    p2.setRenderHint(QPainter.Antialiasing, True)
    p2.setRenderHint(QPainter.SmoothPixmapTransform, True)

    # Subtle gradient
    sgrad = QLinearGradient(0, 0, sw, sh)
    sgrad.setColorAt(0.0, QColor(14, 11, 26))
    sgrad.setColorAt(1.0, QColor(6, 5, 12))
    p2.fillRect(0, 0, sw, sh, sgrad)

    scx, scy = sw / 2, sh / 2
    s_radius = 21

    # Outer neon ring
    p2.setPen(QPen(QColor(229, 9, 20), 2))
    p2.setBrush(QColor(10, 8, 20))
    p2.drawEllipse(QPointF(scx, scy), s_radius, s_radius)

    # Film reel notches (Cyan & Violet)
    for i in range(4):
        angle = i * (2 * math.pi / 4)
        nx = scx + (s_radius - 6) * math.cos(angle)
        ny = scy + (s_radius - 6) * math.sin(angle)
        col = QColor(0, 245, 255) if i % 2 == 0 else QColor(157, 0, 255)
        p2.setBrush(col)
        p2.setPen(Qt.NoPen)
        p2.drawEllipse(QPointF(nx, ny), 1.8, 1.8)

    # Center Play Triangle (Cyan)
    s_tri = QPainterPath()
    s_tr = 7.5
    s_tri.moveTo(scx - s_tr * 0.55, scy - s_tr)
    s_tri.lineTo(scx + s_tr * 0.9, scy)
    s_tri.lineTo(scx - s_tr * 0.55, scy + s_tr)
    s_tri.closeSubpath()

    p2.setPen(QPen(QColor(0, 245, 255, 200), 1))
    p2.setBrush(QColor(0, 245, 255))
    p2.drawPath(s_tri)

    p2.end()

    img2.save("wizard-small-image.bmp", "BMP")
    print("Saved wizard-small-image.bmp: 55x55 (24 bpp)")

if __name__ == "__main__":
    create_wizard_images()
