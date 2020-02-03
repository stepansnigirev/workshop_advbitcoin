For the convenience we've included these files in here. They are coming from somewhere else. To reproduce them:

# `firmware.bin`

wget https://github.com/stepansnigirev/f469-disco/releases/download/1.0.1-alpha/upy-f469disco-empty.bin

# `micropython/lib` folder

This is a copy of this:

https://github.com/diybitcoinhardware/f469-disco/tree/master/libs

# Other files in `micropython` folder

They are the copy of `specter-diy/src` folder with minor changes.

https://github.com/cryptoadvance/specter-diy/

Changes:

- `main.py` renamed to `specter.py` so it doesn't load automatically
- `boot.py` is removed so it always loads in developer mode
