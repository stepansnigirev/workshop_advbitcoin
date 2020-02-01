# Setup

1. Clone this repo:
```
git clone https://github.com/stepansnigirev/workshop_advbitcoin.git
```

2. Connect the board over MicroUSB cable to your computer.
3. Check that it mounts as `PYBFLASH`
4. Check that the board is also visible as a Virtual COM Port:
	- on **MacOS** it should be `/dev/tty.usb<something>` (on my PC it's `/dev/tty.usbmodem3379374D33382`)
	- on **Linux** it should be `/dev/ttyACM0`
	- on **Windows** check `Device Manager` - `COM ports`

## How to connect

Install `pyserial` module:

```
pip3 install pyserial
```

This module includes a very handy tool to talk to serial ports called `miniterm.py`. 
Connect to the board using: 
```
miniterm.py <port_name>
```

On Linux and MacOS you can also use `screen`, on Windows [Putty](https://www.putty.org/) is a good choice.

Other alternatives: `picocom`, `minicom` and many others.

### USB Permissioning on Linux

On some Linux distributions it may be necessary to add additional udev rules in order to allow the REPL to work:

copy the following text to `/etc/udev/rules.d/49-micropython.rules`
```
# f055:9800 - MicroPython board
ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", ENV{ID_MM_DEVICE_IGNORE}="1"
ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", ENV{MTP_NO_PROBE}="1"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", MODE:="0666"
KERNEL=="ttyACM*", ATTRS{idVendor}=="f055", ATTRS{idProduct}=="9800", MODE:="0666"
```

And then restart the udev service:

```bash
sudo udevadm control --reload-rules
```

# Workshop content

Every section has a `README.md` file with explanation and code snippets, and a final `main.py` file that you can use to catch up if you are lost.

1. [Blinky](./1_blinky) - get started with micropython, blinking with LEDs, generate random bytes with TRNG
2. [HD keys](./2_hdkeys) - convert entropy to recovery phrase, get master public key, import to Bitcoin Core
3. [Addresses](./3_addresses) - get first 5 receiving addresses - segwit, nested segwit, legacy. **Bonus:** Taproot addresses.
4. [GUI](./4_gui) - simple address navigation interface
5. [PSBT Transactions](./5_psbt) - get and sign PSBT transaction with hardware wallet
6. [**Bonus:** Taproot](./6_taproot) - sign a transaction with basic Schnorr-Taproot inputs

# References

- Library docs: ???
- [Repository](https://github.com/diybitcoinhardware/f469-disco/) with MicroPython build ([`taproot`](https://github.com/diybitcoinhardware/f469-disco/tree/taproot) branch for experimental taproot support).
- [Tutorial](https://github.com/diybitcoinhardware/f469-disco/tree/master/docs/tutorial/) section of the documentation
- [Youtube playlist](https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5) covering the content of this workshop + some theory
- [GitHub repository](https://github.com/cryptoadvance/specter-diy) of Specter-DIY hardware wallet ([`taproot`](https://github.com/cryptoadvance/specter-diy/tree/taproot) branch for experimental taproot support): 
- [How to](https://github.com/diybitcoinhardware/f469-disco/tree/master/jupyter_kernel)  get Jupyter notebook kernel that works with the board
