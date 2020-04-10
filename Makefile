collect-source:
	curl -L https://github.com/source-foundry/Hack/releases/download/v3.003/Hack-v3.003-ttf.zip -o hack.zip
	unar hack.zip
	cp ttf/* source/
	rm hack.zip
	rm -r ttf
	curl -LO https://osdn.jp/downloads/users/8/8598/rounded-mgenplus-20150602.7z
	unar rounded-mgenplus-20150602.7z
	cp rounded-mgenplus-20150602/rounded-mgenplus-1m-regular.ttf ./source
	cp rounded-mgenplus-20150602/rounded-mgenplus-1m-bold.ttf ./source
	curl -L https://github.com/googlei18n/noto-emoji/raw/master/fonts/NotoEmoji-Regular.ttf -o source/NotoEmoji-Regular.ttf
	curl -LO http://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.zip
	unar dejavu-fonts-ttf-2.37.zip
	mv dejavu-fonts-ttf-2.37/ttf/DejaVuSansMono.ttf ./source/
	mv dejavu-fonts-ttf-2.37/ttf/DejaVuSansMono-Bold.ttf ./source/
	curl -L https://github.com/mirmat/iconsfordevs/raw/master/fonts/iconsfordevs.ttf -o source/iconsfordevs.ttf
	curl -L http://www.unicode.org/Public/12.0.0/ucd/EastAsianWidth.txt -o source/EastAsianWidth.txt
build:
	@fontforge -lang=py -script cica.py 2> /dev/null
