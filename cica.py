#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fontforge
import psMat
import os
import sys
import math
import glob
import width_parser
from datetime import datetime
import argparse

# ASCENT = 850
# DESCENT = 174
ASCENT = 820
DESCENT = 204
WIN_ASCENT = 820
WIN_DESCENT = 204
TYPO_ASCENT = 670
TYPO_DESCENT = -104
TYPO_LINEGAP = 0
HHEA_ASCENT = 855
HHEA_DESCENT = -169
SOURCE = os.getenv('CICA_SOURCE_FONTS_PATH', './sourceFonts')
LICENSE = open('./LICENSE.txt').read()
COPYRIGHT = open('./COPYRIGHT.txt').read()
VERSION = '6.0.0-beta'
FAMILY = 'Cica'
AMBI = 0
SINGLE = 1
DOUBLE = 2

def log(_str):
    """ログ出力
    fontforgeにquietオプションが無いので悲しい
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now + " " + _str)

ignoring_center = [i for i in range(0x20, 0x6ff)]
ignoring_center.extend([
    0x3001, 0x3002, 0x3008, 0x3009, 0x300a, 0x300b, 0x300c, 0x300d,
    0x300e, 0x300f, 0x3010, 0x3011, 0x3014, 0x3015, 0x3016, 0x3017,
    0x3018, 0x3019, 0x301a, 0x301b, 0x301d, 0x301e, 0x3099, 0x309a,
    0x309b, 0x309c,
])

def remove_glyph_from_hack(_font):
    """Rounded Mgen+を採用したいグリフをHackから削除
    """
    glyphs = [
            0x2026, # …
            ]

    for g in glyphs:
        _font.selection.select(g)
        _font.clear()

    return _font

def fix_overflow(glyph):
    """上がASCENTを超えている、または下が-DESCENTを超えているグリフを
    1024x1024の枠にはまるように修正する
    ※全角のグリフのみに実施する
    """
    if glyph.width < 1024:
        return glyph
    if glyph.isWorthOutputting:
        bb = glyph.boundingBox()
        height = bb[3] - bb[1]
        if height > 1024:
            # resize
            scale = 1024 / height
            glyph.transform(psMat.scale(scale, scale))
        bb = glyph.boundingBox()
        bottom = bb[1]
        top = bb[3]
        if bottom < -DESCENT:
            glyph.transform(psMat.translate(0, -DESCENT - bottom))
        elif top > ASCENT:
            glyph.transform(psMat.translate(0, ASCENT - top))
    return glyph


def check_files():
    err = 0
    for f in fonts:
        if not os.path.isfile(os.path.join(SOURCE, f.get('hack'))):
            log('%s not exists.' % f)
            err = 1

        if not os.path.isfile(os.path.join(SOURCE, f.get('mgen_plus'))):
            log('%s not exists.' % f)
            err = 1
    if err > 0:
        sys.exit(err)


def align_to_center(_g):
    """グリフを中央寄せにする
    """
    width = 0

    if _g.width > 700:
        width = 1024
    else:
        width = 512

    _g.width = width
    if _g.encoding in ignoring_center:
        return

    _g.left_side_bearing = _g.right_side_bearing = (_g.left_side_bearing + _g.right_side_bearing)/2
    _g.width = width

    return

def align_to_left(_g):
    """グリフを左寄せにする
    """
    width = _g.width
    _g.left_side_bearing = 0
    _g.width = width

def align_to_right(_g):
    """グリフを右寄せにする
    """
    width = _g.width
    bb = _g.boundingBox()
    left = width - (bb[2] - bb[0])
    _g.left_side_bearing = left
    _g.width = width

def modify_nerd(_g):
    """nerdfontの大きさと位置をCica用に調整
    """
    align_left = [
        0xe0b0, 0xe0b1, 0xe0b4, 0xe0b5, 0xe0b8, 0xe0b9, 0xe0bc,
        0xe0bd, 0xe0c0, 0xe0c1, 0xe0c4, 0xe0c6, 0xe0c8, 0xe0cc, 0xe0cd,
        0xe0d1, 0xe0d2,
    ]
    align_right = [
        0xe0b2, 0xe0b3, 0xe0b6, 0xe0b7, 0xe0b7, 0xe0ba, 0xe0bb, 0xe0be,
        0xe0bf, 0xe0c2, 0xe0c3, 0xe0c5, 0xe0c7, 0xe0ca, 0xe0ce, 0xe0d4,
    ]
    # Powerline
    if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0d4:
        _g.transform(psMat.translate(0, 5))
        _g.width = 1024

        if _g.encoding >= 0xe0b0 and _g.encoding <= 0xe0b7:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0b8 and _g.encoding <= 0xe0bf:
            _g.transform(psMat.compose(psMat.scale(0.8, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024

        if _g.encoding >= 0xe0c0 and _g.encoding <= 0xe0c3:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding >= 0xe0c4 and _g.encoding <= 0xe0c7:
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0c8 or _g.encoding == 0xe0ca:
            _g.transform(psMat.scale(0.7, 1.0))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
        if _g.encoding == 0xe0ce:
            _g.transform(psMat.scale(0.8, 1.0))
            bb = _g.boundingBox()
            left = 1024 - (bb[2] - bb[0])
            _g.left_side_bearing = left
            _g.width = 1024
        if _g.encoding == 0xe0cf:
            _g.transform(psMat.scale(0.9, 1.0))
            align_to_center(_g)
        if _g.encoding == 0xe0d0:
            align_to_center(_g)
        if _g.encoding == 0xe0d1:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            _g.left_side_bearing = 0
            _g.width = 1024
        if _g.encoding == 0xe0d2 or _g.encoding == 0xe0d4:
            _g.transform(psMat.compose(psMat.scale(1.0, 0.982), psMat.translate(0, -1)))
            if _g.encoding in align_right:
                bb = _g.boundingBox()
                left = 1024 - (bb[2] - bb[0])
                _g.left_side_bearing = left
                _g.width = 1024
            if _g.encoding in align_left:
                _g.left_side_bearing = 0
                _g.width = 1024
    elif _g.encoding >= 0xf000 and _g.encoding <= 0xf2e0:
        _g.transform(psMat.compose(psMat.scale(0.75, 0.75), psMat.translate(0, 55)))
        _g.width = 1024
        align_to_center(_g)
    else:
        _g.transform(psMat.translate(0, -55))
        _g.width = 1024
        align_to_center(_g)

    return _g

def modify_iconsfordevs(_g):
    """iconsfordevsの大きさと位置をCica用に調整
    """
    _g.transform(psMat.compose(psMat.scale(2), psMat.translate(0, -126)))
    _g.width = 1024
    align_to_center(_g)
    return _g

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s",
    "--space",
    type=int,
    default=int(os.environ.get("CICA_SPACE", "0")),
    help="全角スペースに枠をつける (0) かつけない (1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-z",
    "--zero",
    type=int,
    default=int(os.environ.get("CICA_ZERO", "0")),
    help="ゼロを dotted(0)、slashed(1)、Hack(2)、blanked(3) から選べます (デフォルト: 0)",
)
parser.add_argument(
    "-a",
    "--asterisk",
    type=int,
    default=int(os.environ.get("CICA_ASTERISK", "0")),
    help="アスタリスクのタイプを radial(0) か star(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-d",
    "--stroked-d",
    type=int,
    default=int(os.environ.get("CICA_STROKED_D", "0")),
    help="Dを stroked(0) か normal(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-v",
    "--vertical-line",
    type=int,
    default=int(os.environ.get("CICA_VERTICAL_LINE", "0")),
    help="縦線を broken(0) か solid(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-w",
    "--ambiguous-width",
    type=int,
    default=int(os.environ.get("CICA_AMBIGUOUS_WIDTH", "0")),
    help="曖昧幅文字幅を single(0) か double(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-e",
    "--ellipsis",
    type=int,
    default=int(os.environ.get("CICA_ELLIPSIS", "0")),
    help="三点リーダー類の幅を single(0) か double(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-i",
    "--emoji",
    type=int,
    default=int(os.environ.get("CICA_EMOJI", "0")),
    help="絵文字類を noto emoji(0) か system(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-m",
    "--modified-m",
    type=int,
    default=int(os.environ.get("CICA_MODIFIED_LOWERCASE_M", "0")),
    help="mの中心の線が short(0) か Hack(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-W",
    "--modified-WM",
    type=int,
    default=int(os.environ.get("CICA_MODIFIED_WM", "0")),
    help="WとMが modified(0) か Hack(1) か選べます (デフォルト: 0)",
)
parser.add_argument(
    "-b",
    "--broken-emdash",
    type=int,
    default=int(os.environ.get("CICA_BROKEN_EMDASH", "0")),
    help="emdashを broken(0) にするか Hack(1) か選べます (デフォルト: 0)",
)
args = parser.parse_args()

print(args)

class Cica:
    def __init__(self, family, name, output_name, weight, weight_name, style_name, font_en, font_jp, italic):
        self.family = family
        self.name = name
        self.output_name = output_name
        self.weight = weight
        self.weight_name = weight_name
        self.style_name = style_name
        self.font_en = fontforge.open(os.path.join(SOURCE, font_en))
        self.font_jp = fontforge.open(os.path.join(SOURCE, font_jp))
        self.italic = italic
        self.nerd = fontforge.open(os.path.join(SOURCE, 'nerd.sfd'))
        self.icons_for_devs = fontforge.open(os.path.join(SOURCE, 'iconsfordevs.ttf'))
        self.wp = width_parser.WidthParser()

    def set_os2_values(self):
        """フォントメタ情報の設定
        """
        weight = self.weight
        style_name = self.style_name
        self.font_jp.os2_weight = weight
        self.font_jp.os2_width = 5
        self.font_jp.os2_fstype = 0
        if style_name == 'Regular':
            self.font_jp.os2_stylemap = 64
        elif style_name == 'Bold':
            self.font_jp.os2_stylemap = 32
        elif style_name == 'Italic':
            self.font_jp.os2_stylemap = 1
        elif style_name == 'Bold Italic':
            self.font_jp.os2_stylemap = 33
        self.font_jp.os2_vendor = 'TMNM'
        self.font_jp.os2_version = 1
        self.font_jp.os2_winascent = WIN_ASCENT
        self.font_jp.os2_winascent_add = False
        self.font_jp.os2_windescent = WIN_DESCENT
        self.font_jp.os2_windescent_add = False

        self.font_jp.os2_typoascent = TYPO_ASCENT
        self.font_jp.os2_typoascent_add = False
        self.font_jp.os2_typodescent = TYPO_DESCENT
        self.font_jp.os2_typodescent_add = False
        self.font_jp.os2_typolinegap = TYPO_LINEGAP

        self.font_jp.hhea_ascent = HHEA_ASCENT
        self.font_jp.hhea_ascent_add = False
        self.font_jp.hhea_descent = HHEA_DESCENT
        self.font_jp.hhea_descent_add = False
        self.font_jp.hhea_linegap = 0
        self.font_jp.os2_panose = (2, 11, int(weight / 100), 9, 2, 2, 3, 2, 2, 7)

    def add_dejavu(self):
        dejavu = None
        weight_name = self.weight_name
        if weight_name == "Regular":
            dejavu = fontforge.open(os.path.join(SOURCE, 'DejaVuSansMono.ttf'))
        elif weight_name == "Bold":
            dejavu = fontforge.open(os.path.join(SOURCE, 'DejaVuSansMono-Bold.ttf'))

        for g in dejavu.glyphs():
            g.transform(psMat.compose(psMat.scale(0.45, 0.45), psMat.translate(-21, 0)))
            g.width = 512

        self.font_jp.importLookups(dejavu, dejavu.gpos_lookups)

        # 0x0300 - 0x036f - Combining Diacritical Marks
        for g in dejavu.glyphs():
            if g.encoding < 0x0300 or g.encoding > 0x036f or g.encoding == 0x0398:
                continue
            else:
                if len(g.references) > 0:
                    anchorPoints = g.anchorPoints
                    g.anchorPoints = ()
                    g.transform(psMat.scale(2.22, 2.22))
                    g.transform(psMat.translate(50, 0))
                    g.width = 512
                    g.anchorPoints = anchorPoints

                if g.encoding <= 0x0304:
                    anchorPoints = g.anchorPoints
                    g.anchorPoints = ()
                    g.transform(psMat.scale(1.2, 1.2))
                    g.transform(psMat.translate(-100, -60))
                    g.width = 512
                    g.anchorPoints = anchorPoints
                elif g.encoding == 0x0305:
                    g.transform(psMat.translate(0, -60))
                elif g.encoding <= 0x0315:
                    g.transform(psMat.translate(0, 0))
                elif g.encoding <= 0x0317:
                    g.transform(psMat.translate(0, 302))
                elif g.encoding <= 0x0319:
                    g.transform(psMat.translate(0, 200))
                elif g.encoding <= 0x031b:
                    g.transform(psMat.translate(0, -60))
                elif g.encoding <= 0x031c:
                    g.transform(psMat.translate(0, 22))
                elif g.encoding <= 0x031f:
                    g.transform(psMat.translate(0, 141))
                elif g.encoding <= 0x0332:
                    g.transform(psMat.translate(0, 90))
                elif g.encoding == 0x0333:
                    g.transform(psMat.compose(psMat.scale(0.9, 0.9), psMat.translate(-415, 29)))
                    g.width = 512
                elif g.encoding <= 0x0338:
                    g.transform(psMat.translate(0, 0))
                elif g.encoding <= 0x033c:
                    g.transform(psMat.translate(0, 138))
                else:
                    g.transform(psMat.translate(0, 0))
                dejavu.selection.select(g.encoding)
                dejavu.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()
        # 0x0370 - 0x03ff - GREEK
        for g in dejavu.glyphs():
            if g.encoding < 0x0370 or g.encoding > 0x03ff or g.encoding == 0x0398:
                continue
            else:
                if len(g.references) == 0:
                    bb = g.boundingBox()
                    g.anchorPoints = (('Anchor-7', 'mark', 256, bb[3] + 20),)
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2100 - 0x214f Letterlike Symbols
        for g in dejavu.glyphs():
            if g.encoding < 0x2100 or g.encoding > 0x214f or g.encoding == 0x2122:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2150 - 0x218f Number Forms
        for g in dejavu.glyphs():
            if g.encoding < 0x2150 or g.encoding > 0x218f:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2190 - 0x21ff Arrows
        for g in dejavu.glyphs():
            if g.encoding < 0x2190 or g.encoding > 0x21ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2200 - 0x22ff Mathematical Operators
        for g in dejavu.glyphs():
            if g.encoding < 0x2200 or g.encoding > 0x22ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        # 0x2300 - 0x23ff Miscellaneous Technical
        for g in dejavu.glyphs():
            if g.encoding < 0x2300 or g.encoding > 0x23ff:
                continue
            else:
                if len(g.references) == 0:
                    dejavu.selection.select(g.encoding)
                    dejavu.copy()
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.paste()
        dejavu.close()


    def vertical_line_to_broken_bar(self):
        """縦線を破線にする
        """
        self.font_jp.selection.select(0x00a6)
        self.font_jp.copy()
        self.font_jp.selection.select(0x007c)
        self.font_jp.paste()

    def emdash_to_broken_dash(self):
        """ダッシュ記号を破線にする
        """
        self.font_jp.selection.select(0x006c)
        self.font_jp.copy()
        self.font_jp.selection.select(0x2014)
        self.font_jp.pasteInto()
        self.font_jp.intersect()

    def zenkaku_space(self):
        """全角スペースに枠をつけて可視化する
        """
        self.font_jp.selection.select(0x2610)
        self.font_jp.copy()
        self.font_jp.selection.select(0x3000)
        self.font_jp.paste()
        self.font_jp.selection.select(0x271a)
        self.font_jp.copy()
        self.font_jp.selection.select(0x3000)
        self.font_jp.pasteInto()
        self.font_jp.intersect()
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def dotted_zero(self):
        """半角数字の0をドットゼロにする
        """
        self.font_jp.selection.select(0x4f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.paste()
        self.font_jp.selection.select(0xb7)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.pasteInto()
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def fix_box_drawings_block_elements(self):
        """罫線やブロック(プログレスバーによく使われる)グリフの左右寄せを調整する
        """
        left = [
            0x2510, 0x2518, 0x2524, 0x2555, 0x2556, 0x2557, 0x255b, 0x255c, 0x255d,
            0x2561, 0x2562, 0x2563, 0x256e, 0x256f, 0x2574, 0x2578,
            0x2589, 0x258a, 0x258b, 0x258c, 0x258d, 0x258e, 0x258f,
            0x2596, 0x2598,
            0xf2510, 0xf2518, 0xf2524, 0xf2555, 0xf2556, 0xf2557, 0xf255b, 0xf255c, 0xf255d,
            0xff2561, 0xf2562, 0xf2563, 0xf256e, 0xf256f, 0xf2574, 0xf2578
        ]
        right = [
            0x250c, 0x2514, 0x251c, 0x2552, 0x2553, 0x2554, 0x2558, 0x2559, 0x255a,
            0x255e, 0x255f, 0x2560, 0x256d, 0x2570, 0x2576, 0x257a,
            0x2590, 0x2595, 0x2597, 0x259d,
            0xf250c, 0xf2514, 0xf251c, 0xf2552, 0xf2553, 0xf2554, 0xf2558, 0xf2559, 0xf255a,
            0xf255e, 0xf255f, 0xf2560, 0xf256d, 0xf2570, 0xf2576, 0xf257a
        ]

        for g in self.font_jp.glyphs():
            if g.encoding < 0x2500:
                continue
            if g.encoding > 0x259f and g.encoding < 0xf2500:
                continue
            if g.encoding in left:
                align_to_left(g)
            elif g.encoding in right:
                align_to_right(g)

    def slashed_zero(self):
        """半角数字の0をスラッシュゼロにする
        """
        self.font_jp.selection.select(0x4f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.paste()
        self.font_jp.selection.select(0x2f)
        self.font_jp.copy()
        self.font_jp.selection.select(0x1)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.scale(0.7, 0.75), psMat.translate(80, 115)))
        self.font_jp.copy()
        self.font_jp.selection.select(0x30)
        self.font_jp.pasteInto()
        self.font_jp.removeOverlap()
        self.font_jp.selection.select(0x1)
        self.font_jp.clear()

    def modify_WM(self):
        """WとMの字体を調整
        """
        self.font_jp.selection.select(0x57)
        self.font_jp.transform(psMat.compose(psMat.scale(0.95, 1.0), psMat.translate(10, 0)))
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)
        self.font_jp.copy()
        self.font_jp.selection.select(0x4d)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.rotate(math.radians(180)), psMat.translate(512, 627)))
        for g in self.font_jp.selection.byGlyphs:
            align_to_center(g)

    def modify_m(self, _weight):
        """mの中央の棒を少し短くする
        """
        m = fontforge.open(os.path.join(SOURCE, 'm-Regular.sfd'))
        if _weight == 'Bold':
            m.close()
            m = fontforge.open(os.path.join(SOURCE, 'm-Bold.sfd'))
        m.selection.select(0x6d)
        m.copy()
        self.font_en.selection.select(0x6d)
        self.font_en.paste()
        for g in m.glyphs():
            if g.encoding == 0x6d:
                anchorPoints = g.anchorPoints
        for g in self.font_en.glyphs():
            if g.encoding == 0x6d:
                g.anchorPoints = anchorPoints

    def add_smalltriangle(self):
        """小さいサンカクを追加
        NerdTree用
        """
        self.font_jp.selection.select(0x25bc)
        self.font_jp.copy()
        self.font_jp.selection.select(0x25be)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.scale(0.64), psMat.translate(0, 68)))
        self.font_jp.copy()
        self.font_jp.selection.select(0x25b8)
        self.font_jp.paste()
        self.font_jp.transform(psMat.rotate(math.radians(90)))
        self.font_jp.transform(psMat.translate(0, 212))

        for g in self.font_jp.glyphs():
            if g.encoding == 0x25be or g.encoding == 0x25b8:
                g.width = 512
                align_to_center(g)


    def reiwa(self, _weight):
        """令和グリフを追加
        """
        reiwa = fontforge.open(os.path.join(SOURCE, 'reiwa.sfd'))
        if _weight == 'Bold':
            reiwa.close()
            reiwa = fontforge.open(os.path.join(SOURCE, 'reiwa-Bold.sfd'))
        for g in reiwa.glyphs():
            if g.isWorthOutputting:
                reiwa.selection.select(0x00)
                reiwa.copy()
                self.font_jp.selection.select(0x32ff)
                self.font_jp.paste()
        reiwa.close()

    def import_svg(self):
        """オリジナルのsvgグリフをインポートする
        """
        files = glob.glob(os.path.join(SOURCE, 'svg/*.svg'))
        for f in files:
            filename, _ = os.path.splitext(os.path.basename(f))
            g = self.font_jp.createChar(int(filename, 16))
            g.width = 1024
            g.vwidth = 1024
            g.clear()
            g.importOutlines(f)
            g.transform(psMat.translate(0, -61))

    def add_notoemoji(self):
        """Noto Emojiを足す
        """
        notoemoji = fontforge.open(os.path.join(SOURCE, 'NotoEmoji-Regular.ttf'))
        for g in notoemoji.glyphs():
            if g.isWorthOutputting and g.encoding > 0x04f9:
                g.transform((0.42,0,0,0.42,0,0))
                align_to_center(g)
                notoemoji.selection.select(g.encoding)
                notoemoji.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()
        notoemoji.close()

    def add_gopher(self):
        """半身Gopherくんを追加
        """
        gopher = fontforge.open(os.path.join(SOURCE, 'gopher.sfd'))
        for g in gopher.glyphs():
            if g.isWorthOutputting:
                gopher.selection.select(0x40)
                gopher.copy()
                self.font_jp.selection.select(0xE160)
                self.font_jp.paste()
                g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
                gopher.copy()
                self.font_jp.selection.select(0xE161)
                self.font_jp.paste()
        gopher.close()

    def resize_supersub(self):
        """上付文字、下付文字を調整して可読性を上げる
        """
        superscripts = [
                {"src": 0x0031, "dest": 0x00b9}, {"src": 0x0032, "dest": 0x00b2},
                {"src": 0x0033, "dest": 0x00b3}, {"src": 0x0030, "dest": 0x2070},
                {"src": 0x0069, "dest": 0x2071}, {"src": 0x0034, "dest": 0x2074},
                {"src": 0x0037, "dest": 0x2077}, {"src": 0x0038, "dest": 0x2078},
                {"src": 0x0039, "dest": 0x2079}, {"src": 0x002b, "dest": 0x207a},
                {"src": 0x002d, "dest": 0x207b}, {"src": 0x003d, "dest": 0x207c},
                {"src": 0x0028, "dest": 0x207d}, {"src": 0x0029, "dest": 0x207e},
                {"src": 0x006e, "dest": 0x207f},
                # ↓上付きの大文字
                {"src": 0x0041, "dest": 0x1d2c}, {"src": 0x00c6, "dest": 0x1d2d},
                {"src": 0x0042, "dest": 0x1d2e}, {"src": 0x0044, "dest": 0x1d30},
                {"src": 0x0045, "dest": 0x1d31}, {"src": 0x018e, "dest": 0x1d32},
                {"src": 0x0047, "dest": 0x1d33}, {"src": 0x0048, "dest": 0x1d34},
                {"src": 0x0049, "dest": 0x1d35}, {"src": 0x004a, "dest": 0x1d36},
                {"src": 0x004b, "dest": 0x1d37}, {"src": 0x004c, "dest": 0x1d38},
                {"src": 0x004d, "dest": 0x1d39}, {"src": 0x004e, "dest": 0x1d3a},
                ## ↓REVERSED N なのでNを左右反転させる必要あり
                {"src": 0x004e, "dest": 0x1d3b, "reversed": True},
                {"src": 0x004f, "dest": 0x1d3c}, {"src": 0x0222, "dest": 0x1d3d},
                {"src": 0x0050, "dest": 0x1d3e}, {"src": 0x0052, "dest": 0x1d3f},
                {"src": 0x0054, "dest": 0x1d40}, {"src": 0x0055, "dest": 0x1d41},
                {"src": 0x0057, "dest": 0x1d42},
                # ↓上付きの小文字
                {"src": 0x0061, "dest": 0x1d43}, {"src": 0x0250, "dest": 0x1d44},
                {"src": 0x0251, "dest": 0x1d45}, {"src": 0x1d02, "dest": 0x1d46},
                {"src": 0x0062, "dest": 0x1d47}, {"src": 0x0064, "dest": 0x1d48},
                {"src": 0x0065, "dest": 0x1d49}, {"src": 0x0259, "dest": 0x1d4a},
                {"src": 0x025b, "dest": 0x1d4b}, {"src": 0x025c, "dest": 0x1d4c},
                {"src": 0x0067, "dest": 0x1d4d},
                ## ↓TURNED i なので 180度回す必要あり
                {"src": 0x0069, "dest": 0x1d4e, "turned": True},
                {"src": 0x006b, "dest": 0x1d4f}, {"src": 0x006d, "dest": 0x1d50},
                {"src": 0x014b, "dest": 0x1d51}, {"src": 0x006f, "dest": 0x1d52},
                {"src": 0x0254, "dest": 0x1d53}, {"src": 0x1d16, "dest": 0x1d54},
                {"src": 0x1d17, "dest": 0x1d55}, {"src": 0x0070, "dest": 0x1d56},
                {"src": 0x0074, "dest": 0x1d57}, {"src": 0x0075, "dest": 0x1d58},
                {"src": 0x1d1d, "dest": 0x1d59}, {"src": 0x026f, "dest": 0x1d5a},
                {"src": 0x0076, "dest": 0x1d5b}, {"src": 0x1d25, "dest": 0x1d5c},
                {"src": 0x03b2, "dest": 0x1d5d}, {"src": 0x03b3, "dest": 0x1d5e},
                {"src": 0x03b4, "dest": 0x1d5f}, {"src": 0x03c6, "dest": 0x1d60},
                {"src": 0x03c7, "dest": 0x1d61},
                {"src": 0x0056, "dest": 0x2c7d}, {"src": 0x0068, "dest": 0x02b0},
                {"src": 0x0266, "dest": 0x02b1}, {"src": 0x006a, "dest": 0x02b2},
                {"src": 0x006c, "dest": 0x02e1}, {"src": 0x0073, "dest": 0x02e2},
                {"src": 0x0078, "dest": 0x02e3}, {"src": 0x0072, "dest": 0x02b3},
                {"src": 0x0077, "dest": 0x02b7}, {"src": 0x0079, "dest": 0x02b8},
                {"src": 0x0063, "dest": 0x1d9c}, {"src": 0x0066, "dest": 0x1da0},
                {"src": 0x007a, "dest": 0x1dbb}, {"src": 0x0061, "dest": 0x00aa},
                {"src": 0x0252, "dest": 0x1d9b}, {"src": 0x0255, "dest": 0x1d9d},
                {"src": 0x00f0, "dest": 0x1d9e}, {"src": 0x025c, "dest": 0x1d9f},
                {"src": 0x025f, "dest": 0x1da1}, {"src": 0x0261, "dest": 0x1da2},
                {"src": 0x0265, "dest": 0x1da3}, {"src": 0x0268, "dest": 0x1da4},
                {"src": 0x0269, "dest": 0x1da5}, {"src": 0x026a, "dest": 0x1da6},
                {"src": 0x1d7b, "dest": 0x1da7}, {"src": 0x029d, "dest": 0x1da8},
                {"src": 0x026d, "dest": 0x1da9}, {"src": 0x1d85, "dest": 0x1daa},
                {"src": 0x029f, "dest": 0x1dab}, {"src": 0x0271, "dest": 0x1dac},
                {"src": 0x0270, "dest": 0x1dad}, {"src": 0x0272, "dest": 0x1dae},
                {"src": 0x0273, "dest": 0x1daf}, {"src": 0x0274, "dest": 0x1db0},
                {"src": 0x0275, "dest": 0x1db1}, {"src": 0x0278, "dest": 0x1db2},
                {"src": 0x0282, "dest": 0x1db3}, {"src": 0x0283, "dest": 0x1db4},
                {"src": 0x01ab, "dest": 0x1db5}, {"src": 0x0289, "dest": 0x1db6},
                {"src": 0x028a, "dest": 0x1db7}, {"src": 0x1d1c, "dest": 0x1db8},
                {"src": 0x028b, "dest": 0x1db9}, {"src": 0x028c, "dest": 0x1dba},
                {"src": 0x0290, "dest": 0x1dbc}, {"src": 0x0291, "dest": 0x1dbd},
                {"src": 0x0292, "dest": 0x1dbe}, {"src": 0x03b8, "dest": 0x1dbf},

        ]
        subscripts = [
                {"src": 0x0069, "dest": 0x1d62}, {"src": 0x0072, "dest": 0x1d63},
                {"src": 0x0075, "dest": 0x1d64}, {"src": 0x0076, "dest": 0x1d65},
                {"src": 0x03b2, "dest": 0x1d66}, {"src": 0x03b3, "dest": 0x1d67},
                {"src": 0x03c1, "dest": 0x1d68}, {"src": 0x03c6, "dest": 0x1d69},
                {"src": 0x03c7, "dest": 0x1d6a}, {"src": 0x006a, "dest": 0x2c7c},
                {"src": 0x0030, "dest": 0x2080}, {"src": 0x0031, "dest": 0x2081},
                {"src": 0x0032, "dest": 0x2082}, {"src": 0x0033, "dest": 0x2083},
                {"src": 0x0034, "dest": 0x2084}, {"src": 0x0035, "dest": 0x2085},
                {"src": 0x0036, "dest": 0x2086}, {"src": 0x0037, "dest": 0x2087},
                {"src": 0x0038, "dest": 0x2088}, {"src": 0x0039, "dest": 0x2089},
                {"src": 0x002b, "dest": 0x208a}, {"src": 0x002d, "dest": 0x208b},
                {"src": 0x003d, "dest": 0x208c}, {"src": 0x0028, "dest": 0x208d},
                {"src": 0x0029, "dest": 0x208e}, {"src": 0x0061, "dest": 0x2090},
                {"src": 0x0065, "dest": 0x2091}, {"src": 0x006f, "dest": 0x2092},
                {"src": 0x0078, "dest": 0x2093}, {"src": 0x0259, "dest": 0x2094},
                {"src": 0x0068, "dest": 0x2095}, {"src": 0x006b, "dest": 0x2096},
                {"src": 0x006c, "dest": 0x2097}, {"src": 0x006d, "dest": 0x2098},
                {"src": 0x006e, "dest": 0x2099}, {"src": 0x0070, "dest": 0x209a},
                {"src": 0x0073, "dest": 0x209b}, {"src": 0x0074, "dest": 0x209c}
        ]

        for g in superscripts:
            self.font_jp.selection.select(g["src"])
            self.font_jp.copy()
            self.font_jp.selection.select(g["dest"])
            self.font_jp.paste()
        for g in subscripts:
            self.font_jp.selection.select(g["src"])
            self.font_jp.copy()
            self.font_jp.selection.select(g["dest"])
            self.font_jp.paste()

        for g in self.font_jp.glyphs("encoding"):
            if g.encoding > 0x2c7d:
                continue
            elif self.in_scripts(g.encoding, superscripts):
                if g.encoding == 0x1d5d or g.encoding == 0x1d61:
                    g.transform(psMat.scale(0.70, 0.70))
                elif g.encoding == 0x1d3b:
                    g.transform(psMat.scale(0.75, 0.75))
                    g.transform(psMat.compose(psMat.scale(-1, 1), psMat.translate(g.width, 0)))
                elif g.encoding == 0x1d4e:
                    g.transform(psMat.scale(0.75, 0.75))
                    g.transform(psMat.rotate(3.14159))
                    g.transform(psMat.translate(0, 512))
                else:
                    g.transform(psMat.scale(0.75, 0.75))
                bb = g.boundingBox()
                g.transform(psMat.translate(0, 244))
                align_to_center(g)
            elif self.in_scripts(g.encoding, subscripts):
                if g.encoding == 0x1d66 or g.encoding == 0x1d6a:
                    g.transform(psMat.scale(0.70, 0.70))
                else:
                    g.transform(psMat.scale(0.75, 0.75))
                bb = g.boundingBox()
                y = -144
                if bb[1] < -60: # DESCENT - 144
                    y = -60
                g.transform(psMat.translate(0, y))
                align_to_center(g)

    def in_scripts(self, encoding, scripts):
        """scriptsの中にencodingが含まれるかをチェックする
        """
        for s in scripts:
            if encoding == s["dest"]:
                return True
        return False

    def modify_ellipsis(self):
        """3点リーダーを半角にする
        DejaVuSansMono の U+22EF(⋯) をU+2026(…)、U+22EE(⋮)、U+22F0(⋰)、U+22F1(⋱)
        にコピーした上で回転させて生成

        三点リーダの文字幅について · Issue #41 · miiton/Cica https://github.com/miiton/Cica/issues/41
        """
        self.font_jp.selection.select(0x22ef)
        self.font_jp.copy()
        self.font_jp.selection.select(0x2026)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22ee)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22f0)
        self.font_jp.paste()
        self.font_jp.selection.select(0x22f1)
        self.font_jp.paste()
        for g in self.font_jp.glyphs("encoding"):
            if g.encoding < 0x22ee:
                continue
            elif g.encoding > 0x22f1:
                break
            elif g.encoding == 0x22ee:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(90)), psMat.inverse(trcen)))
                g.transform(rotcen)
            elif g.encoding == 0x22f0:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(45)), psMat.inverse(trcen)))
                g.transform(rotcen)
            elif g.encoding == 0x22f1:
                bb = g.boundingBox()
                cx = (bb[2] + bb[0]) / 2
                cy = (bb[3] + bb[1]) / 2
                trcen = psMat.translate(-cx, -cy)
                rotcen = psMat.compose(trcen, psMat.compose(psMat.rotate(math.radians(-45)), psMat.inverse(trcen)))
                g.transform(rotcen)

    def stroked_d(self):
        """Dを横線入りのĐにする
        """
        self.font_jp.selection.select(0x110)
        self.font_jp.copy()
        self.font_jp.selection.select(0x44)
        self.font_jp.paste()

    def asterisk(self, up = 200):
        """アスタリスクを放射状にする
        """
        self.font_jp.selection.select(0xffbc2)
        self.font_jp.copy()
        self.font_jp.selection.select(0x2a)
        self.font_jp.paste()
        self.font_jp.transform(psMat.compose(psMat.scale(0.5, 0.5), psMat.translate(0, up)))
        if self.weight_name == 'Bold':
            self.font_jp.stroke("circular", 20, 'butt', 'round', 'removeinternal')


    def build(self, emoji):
        log('transform font_en')
        for g in self.font_en.glyphs():
            g.transform((0.42,0,0,0.42,0,0))
            align_to_center(g)

        if args.modified_m == 0:
            self.modify_m(self.weight_name)
        log('transform font_jp')
        for g in self.font_jp.glyphs():
            g.transform((0.91,0,0,0.91,0,0))
            full_half_threshold = 700
            if self.italic:
                g.transform(psMat.skew(0.25))
                skew_amount = g.font.ascent * 0.91 * 0.25
                g.width = g.width + skew_amount
                full_half_threshold += skew_amount
            if g.width > full_half_threshold:
                width = 1024
            else:
                width = 512
            g.transform(psMat.translate((width - g.width)/2, 0))
            g.width = width
            if g.encoding in ignoring_center:
                pass
            else:
                align_to_center(g)

        # 0x2715 -> 0xd7 : 乗算記号
        self.font_jp.selection.select(0x2715)
        self.font_jp.copy()
        self.font_jp.selection.select(0xd7)
        self.font_jp.paste()
        # 0xff1a + 0xff0d -> 0xf7 : 除算記号
        self.font_jp.selection.select(0xff1a)
        self.font_jp.copy()
        self.font_jp.selection.select(0xf7)
        self.font_jp.paste()
        self.font_jp.selection.select(0xff0d)
        self.font_jp.copy()
        self.font_jp.selection.select(0xf7)
        self.font_jp.pasteInto()
        # 0xff0b + 0xff3f -> 0xb1 : プラスマイナス記号
        self.font_jp.selection.select(0xff0b)
        self.font_jp.copy()
        self.font_jp.selection.select(0xb1)
        self.font_jp.paste()
        self.font_jp.selection.select(0xff3f)
        self.font_jp.copy()
        self.font_jp.selection.select(0xb1)
        self.font_jp.pasteInto()

        log('modify border glyphs')
        for g in self.font_en.glyphs():
            if g.isWorthOutputting:
                if self.italic:
                    g.transform(psMat.skew(0.25))
                if g.encoding >= 0x2500 and g.encoding <= 0x257f:
                    # 全角の罫線を0xf0000以降に退避
                    self.font_jp.selection.select(g.encoding)
                    self.font_jp.copy()
                    self.font_jp.selection.select(g.encoding + 0xf0000)
                    self.font_jp.paste()
                if g.encoding >= 0x2500 and g.encoding <= 0x25af:
                    g.transform(psMat.compose(psMat.scale(1.024, 1.024), psMat.translate(0, -30)))
                    align_to_center(g)
                self.font_en.selection.select(g.encoding)
                self.font_en.copy()
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()

        log('modify nerd glyphs')
        for g in self.nerd.glyphs():
            if g.encoding < 0xe0a0 or g.encoding > 0xfd46:
                continue
            g = modify_nerd(g)
            self.nerd.selection.select(g.encoding)
            self.nerd.copy()
            if g.encoding >= 0xf500:
                # Material Design IconsはNerd Fontsに従うとアラビア文字等を壊して
                # しまうので、0xf0000〜に配置する
                self.font_jp.selection.select(g.encoding + 0xf0000)
                self.font_jp.paste()
            else:
                self.font_jp.selection.select(g.encoding)
                self.font_jp.paste()

        log('modify icons_for_devs glyphs')
        for g in self.icons_for_devs.glyphs():
            if g.encoding < 0xe900 or g.encoding > 0xe950:
                continue
            g = modify_iconsfordevs(g)
            self.icons_for_devs.selection.select(g.encoding)
            self.icons_for_devs.copy()
            self.font_jp.selection.select(g.encoding)
            self.font_jp.paste()

        self.fix_box_drawings_block_elements()
        if args.space == 0:
            self.zenkaku_space()

        if args.zero == 0:
            self.dotted_zero()
        elif args.zero == 1:
            self.slashed_zero()
        elif args.zero == 2:
            pass

        if args.stroked_d == 0:
            self.stroked_d()

        if args.modified_WM == 0:
            self.modify_WM()

        if args.vertical_line == 0:
            self.vertical_line_to_broken_bar()
        elif args.vertical_line == 1:
            pass

        if args.broken_emdash == 0:
            self.emdash_to_broken_dash()
        self.reiwa(self.weight_name)
        self.add_gopher()
        if args.ellipsis == 0:
            self.modify_ellipsis()
        elif args.ellipsis == 1:
            pass

        if args.asterisk == 0:
            self.asterisk(200)  # 200 or 300   ##
        elif args.asterisk == 1:
            pass

        if args.emoji == 0:
            self.add_notoemoji()
        elif args.emoji == 1:
            pass

        self.add_smalltriangle()
        self.add_dejavu()
        self.resize_supersub()

        log("fix_overflow()")
        for g in self.font_jp.glyphs():
            g = fix_overflow(g)
        log("import_svg()")
        self.import_svg()
        self.font_jp.ascent = ASCENT
        self.font_jp.descent = DESCENT
        self.font_jp.upos = 45
        self.font_jp.fontname = self.family
        self.font_jp.familyname = self.family
        self.font_jp.fullname = self.name
        self.font_jp.weight = self.weight_name
        self.set_os2_values()
        self.font_jp.appendSFNTName(0x411,0, COPYRIGHT)
        self.font_jp.appendSFNTName(0x411,1, self.family)
        self.font_jp.appendSFNTName(0x411,2, self.style_name)
        self.font_jp.appendSFNTName(0x411,4, self.name)
        self.font_jp.appendSFNTName(0x411,5, "Version " + VERSION)
        self.font_jp.appendSFNTName(0x411,6, self.family + "-" + self.weight_name)
        self.font_jp.appendSFNTName(0x411,13, LICENSE)
        self.font_jp.appendSFNTName(0x411,16, self.family)
        self.font_jp.appendSFNTName(0x411,17, self.style_name)
        self.font_jp.appendSFNTName(0x409,0, COPYRIGHT)
        self.font_jp.appendSFNTName(0x409,1, self.family)
        self.font_jp.appendSFNTName(0x409,2, self.style_name)
        self.font_jp.appendSFNTName(0x409,3, VERSION + ";" + self.family + "-" + self.style_name)
        self.font_jp.appendSFNTName(0x409,4, self.name)
        self.font_jp.appendSFNTName(0x409,5, "Version " + VERSION)
        self.font_jp.appendSFNTName(0x409,6, self.name)
        self.font_jp.appendSFNTName(0x409,13, LICENSE)
        self.font_jp.appendSFNTName(0x409,16, self.family)
        self.font_jp.appendSFNTName(0x409,17, self.style_name)
        if emoji:
            fontpath = './dist/%s' % self.output_name
        else:
            fontpath = './dist/noemoji/%s' % self.output_name

        self.font_jp.generate(fontpath)

        self.font_jp.close()
        self.font_en.close()
        self.nerd.close()
        self.icons_for_devs.close()

fonts = [
    {
        'family': FAMILY,
        'name': FAMILY + '-Regular',
        'filename': FAMILY + '-Regular.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Regular',
        'hack': 'Hack-Regular.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-RegularItalic',
        'filename': FAMILY + '-RegularItalic.ttf',
        'weight': 400,
        'weight_name': 'Regular',
        'style_name': 'Italic',
        'hack': 'Hack-Regular.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-regular.ttf',
        'italic': True,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-Bold',
        'filename': FAMILY + '-Bold.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'italic': False,
    }, {
        'family': FAMILY,
        'name': FAMILY + '-BoldItalic',
        'filename': FAMILY + '-BoldItalic.ttf',
        'weight': 700,
        'weight_name': 'Bold',
        'style_name': 'Bold Italic',
        'hack': 'Hack-Bold.ttf',
        'mgen_plus': 'rounded-mgenplus-1m-bold.ttf',
        'italic': True,
    }
]


def main():
    for _f in fonts:
        cica = Cica(_f["family"],
                _f["name"],
                _f["filename"],
                _f["weight"],
                _f["weight_name"],
                _f["style_name"],
                _f["hack"],
                _f["mgen_plus"],
                _f["italic"]
                )
        cica.build(True)

if __name__ == '__main__':
    main()
