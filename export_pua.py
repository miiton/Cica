#!/usr/bin/env python
# -*- coding: utf-8 -*-
import fontforge


cica = fontforge.open('./dist/Cica-Regular.ttf')
for g in cica.glyphs():
    if g.isWorthOutputting and g.encoding >= 0xe0a0 and g.encoding <= 0xf4a8:
        print('<div class="glyph"><div class="glyphUnicode">%s</div><div class="glyphDisplay">&#%s;</div></div>' % (hex(g.unicode), g.encoding))
