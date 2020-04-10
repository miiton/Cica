FROM ubuntu:18.04

ENV HACK_VERSION v3.003
ENV MGENPLUS_VERSION 20150602
ENV NOTO_EMOJI_VERSION master
ENV DEJAVU_VERSION 2.37
ENV ICONSFORDEVS_VERSION master

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common fontforge unar git curl && \
    mkdir /work
WORKDIR /work
COPY source source
RUN curl -L https://github.com/source-foundry/Hack/releases/download/$HACK_VERSION/Hack-$HACK_VERSION-ttf.zip -o /tmp/hack.zip && \
    unar /tmp/hack.zip -o /tmp/hack && cp /tmp/hack/ttf/* source/ && \
    curl -L https://osdn.jp/downloads/users/8/8598/rounded-mgenplus-$MGENPLUS_VERSION.7z -o /tmp/rounded-mgenplus.7z && \
    unar /tmp/rounded-mgenplus.7z -o /tmp && \
    cp /tmp/rounded-mgenplus/rounded-mgenplus-1m-regular.ttf source/ && \
    cp /tmp/rounded-mgenplus/rounded-mgenplus-1m-bold.ttf source/ && \
    curl -L https://github.com/googlei18n/noto-emoji/raw/$NOTO_EMOJI_VERSION/fonts/NotoEmoji-Regular.ttf -o source/NotoEmoji-Regular.ttf && \
    curl -L http://sourceforge.net/projects/dejavu/files/dejavu/$DEJAVU_VERSION/dejavu-fonts-ttf-$DEJAVU_VERSION.zip -o /tmp/dejavu.zip && \
    unar /tmp/dejavu.zip -o /tmp && \
    cp /tmp/dejavu-fonts-ttf-$DEJAVU_VERSION/ttf/DejaVuSansMono.ttf source/ && \
    cp /tmp/dejavu-fonts-ttf-$DEJAVU_VERSION/ttf/DejaVuSansMono-Bold.ttf source/ && \
    curl -L https://github.com/mirmat/iconsfordevs/raw/$ICONSFORDEVS_VERSION/fonts/iconsfordevs.ttf -o source/iconsfordevs.ttf && \
    curl -L http://www.unicode.org/Public/12.0.0/ucd/EastAsianWidth.txt -o source/EastAsianWidth.txt

COPY cica.py cica.py
COPY width_parser.py width_parser.py
COPY LICENSE.txt LICENSE.txt
COPY COPYRIGHT.txt COPYRIGHT.txt

ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh
