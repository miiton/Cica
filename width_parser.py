#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

# 0: ambi, 1: half, 2: wide
# glyphs = [
#         {0xe0b3: 0},
#         {0xe0b3: 0},
#         {0xe0b3: 0},
#         {0xe0b3: 0},
# ]

SOURCE = os.getenv('CICA_SOURCE_FONTS_PATH', './sourceFonts')

class WidthParser:
    """グリフの幅をunicode.orgのデータから判定する

    Examples
    --------
    >>> wp = WidthParser()
    >>> wp.width(0x3000)
    2
    """
    def __init__(self):
        self.width_type = {
                'A': 0,
                'H': 1, 'N': 1, 'Na': 1,
                'F': 2, 'W': 2,
        }
        self.dictionary = {}
        self.execute()


    def parse_line(self, line):
        a = line.split(";")
        u = a[0].split("..")
        width = self.width_type[a[1]]
        start = int(u[0], 16)
        if len(u) == 2:
            finish = int(u[1], 16)
            for i in range(start, finish + 1):
                self.dictionary[i] = width
        else:
            self.dictionary[start] = width


    def execute(self):
        """EastAsianWidth.txtをパースする
        """
        pattern = '^([^ ]+) *#.*$'
        regex = re.compile(pattern)
        data = open(os.path.join(SOURCE, 'EastAsianWidth.txt'), "r")

        # 一行ずつ読み込んでは表示する
        for line in data:
            match = regex.match(line)
            if match:
                self.parse_line(match.group(1))

        # ファイルをクローズする
        data.close()

    def width(self, uni):
        try:
            return self.dictionary[uni]
        except:
            pass




if __name__ == '__main__':
    wp = WidthParser()
    print(wp.width(0xb1))
