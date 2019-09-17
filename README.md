# Installation

`pip install -r requirements.txt`

## Install Tesseract 4

### Ubuntu 16.04 (https://github.com/tesseract-ocr/tesseract/wiki)

`sudo add-apt-repository ppa:alex-p/tesseract-ocr`

`sudo apt-get update`

`sudo apt install tesseract-ocr tesseract-langpack-deu`

### Mac OSX (https://github.com/tesseract-ocr/tesseract/issues/1453)

`brew install automake autoconf autoconf-archive libtool`

`brew install pkgconfig`

`brew install icu4c`

`brew install leptonica`

`brew install gcc`

`ln -hfs /usr/local/Cellar/icu4c/60.2 /usr/local/opt/icu4c`

`git clone https://github.com/tesseract-ocr/tesseract/`

`cd tesseract`

`./autogen.sh`
`brew info icu4c`

`./configure \
  CPPFLAGS=-I/usr/local/opt/icu4c/include \
  LDFLAGS=-L/usr/local/opt/icu4c/lib`

`make -j`

`sudo make install`

`sudo update_dyld_shared_cache`

`make training`

### NLTK and Space packages

`python -m nltk.downloader punkt averaged_perceptron_tagger`

`python -m spacy download en`
