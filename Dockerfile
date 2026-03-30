FROM ubuntu:22.04

ENV HACK_VERSION v3.003
ENV HACK_ARCHIVE_HASH 0c2604631b1f055041c68a0e09ae4801acab6c5072ba2db6a822f53c3f8290ac
ENV MGENPLUS_GDRIVE_ID 1NWZvbjzMDIJyzwpTULi4Lk7uzayU7F7j
ENV MGENPLUS_ARCHIVE_HASH ecea6764973d93936238f1c06ed246310bec320f63f350c2bdb7e8d1feee25cc
ENV NOTO_EMOJI_VERSION v2.034
ENV NOTO_EMOJI_FILE_HASH 415dc6290378574135b64c808dc640c1df7531973290c4970c51fdeb849cb0c5
ENV DEJAVU_VERSION 2.37
ENV DEJAVU_ARCHIVE_HASH 7576310b219e04159d35ff61dd4a4ec4cdba4f35c00e002a136f00e96a908b0a
ENV ICONSFORDEVS_VERSION 6a0e325e057e29b341ac4733e8a05953fa614aa2
ENV ICONSFORDEVS_FILE_HASH 87e6cd72233dfb4919feb957a4aee3ace140ee78ea1d9741fbaa4027589d2988
ENV CICA_SOURCE_FONTS_PATH /work/sourceFonts

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install \
    software-properties-common fontforge unar git curl python3 python3-pip && \
    pip3 install gdown && \
    mkdir /work
WORKDIR /work
COPY sourceFonts sourceFonts
RUN curl --fail -L https://github.com/source-foundry/Hack/releases/download/$HACK_VERSION/Hack-$HACK_VERSION-ttf.zip -o /tmp/hack.zip && \
    echo "${HACK_ARCHIVE_HASH}  /tmp/hack.zip" | shasum -c && \
    unar /tmp/hack.zip -o /tmp/hack && cp /tmp/hack/ttf/* sourceFonts/ && \
    gdown https://drive.google.com/uc?id=$MGENPLUS_GDRIVE_ID -O /tmp/rounded-mgenplus.7z && \
    echo "${MGENPLUS_ARCHIVE_HASH}  /tmp/rounded-mgenplus.7z" | shasum -c && \
    unar /tmp/rounded-mgenplus.7z -o /tmp && \
    cp /tmp/rounded-mgenplus/rounded-mgenplus-1m-regular.ttf sourceFonts/ && \
    cp /tmp/rounded-mgenplus/rounded-mgenplus-1m-bold.ttf sourceFonts/ && \
    curl --fail -L https://github.com/googlefonts/noto-emoji/blob/$NOTO_EMOJI_VERSION/fonts/NotoEmoji-Regular.ttf?raw=true -o sourceFonts/NotoEmoji-Regular.ttf && \
    echo "${NOTO_EMOJI_FILE_HASH}  sourceFonts/NotoEmoji-Regular.ttf" | shasum -c && \
    curl --fail -L http://sourceforge.net/projects/dejavu/files/dejavu/$DEJAVU_VERSION/dejavu-fonts-ttf-$DEJAVU_VERSION.zip -o /tmp/dejavu.zip && \
    echo "${DEJAVU_ARCHIVE_HASH}  /tmp/dejavu.zip" | shasum -c && \
    unar /tmp/dejavu.zip -o /tmp && \
    cp /tmp/dejavu-fonts-ttf-$DEJAVU_VERSION/ttf/DejaVuSansMono.ttf sourceFonts/ && \
    cp /tmp/dejavu-fonts-ttf-$DEJAVU_VERSION/ttf/DejaVuSansMono-Bold.ttf sourceFonts/ && \
    curl --fail -L https://github.com/mirmat/iconsfordevs/raw/$ICONSFORDEVS_VERSION/fonts/iconsfordevs.ttf -o sourceFonts/iconsfordevs.ttf && \
    echo "${ICONSFORDEVS_FILE_HASH}  sourceFonts/iconsfordevs.ttf" | shasum -c

COPY cica.py cica.py
COPY LICENSE.txt LICENSE.txt
COPY COPYRIGHT.txt COPYRIGHT.txt

ADD entrypoint.sh /usr/local/bin/entrypoint.sh

ENTRYPOINT entrypoint.sh
