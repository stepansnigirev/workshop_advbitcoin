# Writing GUI with LittlevGL library

[LittlevGL](https://littlevgl.com/) is a very powerful graphics library with a lot of widgets and very rich functionality. It is open-source with MIT license, supports antialiasing, customization and written in an object-oriented way even though it is in C. Recently they also made MicroPython bindings to the library so we can easily write our GUI in MicroPython (`lvgl` module).

In the [previous part](../1_bitcoin) of the tutorial we were able to derive addresses from the recovery phrase, now it's time to write a small GUI that would display these addresses.

**TL;DR**: Check out the [result in the simulator](https://diybitcoinhardware.com/f469-disco/simulator/?script=https://raw.githubusercontent.com/diybitcoinhardware/f469-disco/master/docs/tutorial/2_addresses_gui/main.py).

## Hello lvgl

Let's start with something simple. We will turn on the screen and print a single address to it.

In all our builds we have a `display` module that intializes the display, registers the drivers and does all preparation steps. We only need to call `display.init()` in the beggining of the program and our display is ready to work with. On the real hardware there is one more trick that we will need to do, but we will keep it for [later](../4_gui).

Here is our first GUI that prints the address:

```python
import display
import lvgl as lv
from bitcoin import bip32, script
from bitcoin.networks import NETWORKS

# parse xpub
xpub = bip32.HDKey.from_base58("vpub5ZEy1ogdkmtEHB4kRUZ6o6r7RREFckx7Mh4df39FEDPYkyQYLDnTqV68z7Knnmj5eGT9res4JfQbXEMiPrnzRGKS62zQPa4uNsXM1aS8iyP")

def get_address(idx, change=False, network=NETWORKS["test"]):
    """Returns the receiving/change address for network"""
    # we can also derive a pubkey by passing a list of integers instead of a string
    child = xpub.derive([int(change), idx])
    sc = script.p2wpkh(child)
    return sc.address(network)

display.init()
# get active screen
scr = lv.scr_act()
# draw a label on this screen
lbl = lv.label(scr)
# set text of the label
lbl.set_text(get_address(0))
# position it in the center of the screen
lbl.align(None, lv.ALIGN.CENTER, 0, 0)
# align text to the center of the label
lbl.set_align(lv.label.ALIGN.CENTER)
```

If you are interested in what you can do with littlevgl - what object types are available, how to style them etc, check out the [documentation](https://docs.littlevgl.com/en/html/index.html) of this library. They also have MicroPython examples.

## Make it alive

It's time to add two buttons and implement navigation between addresses:

```python
current_index = 0

def next_cb(obj, event):
    """Callback for "Next" button"""
    if event == lv.EVENT.RELEASED:
        global current_index
        current_index += 1
        lbl.set_text(get_address(current_index))
        # realign
        lbl.align(None, lv.ALIGN.CENTER, 0, 0)

def prev_cb(obj, event):
    """Callback for "Previous" button"""
    if event == lv.EVENT.RELEASED:
        global current_index
        # only decrease if index remains positive
        if current_index > 0:
            current_index -= 1
            lbl.set_text(get_address(current_index))
            # realign
            lbl.align(None, lv.ALIGN.CENTER, 0, 0)

# create the next button
btn = lv.btn(scr)
# create a label on the button
btn_lbl = lv.label(btn)
btn_lbl.set_text("Next")
btn.set_width(100)
btn.align(lbl, lv.ALIGN.OUT_BOTTOM_MID, 60, 30)
# add callback
btn.set_event_cb(next_cb)

# create the prev button
btn = lv.btn(scr)
# create a label on the button
btn_lbl = lv.label(btn)
btn_lbl.set_text("Previous")
btn.set_width(100)
btn.align(lbl, lv.ALIGN.OUT_BOTTOM_MID, -60, 30)
# add callback
btn.set_event_cb(prev_cb)
```

## Screen class

Looks good, but using `global` is not great. It also makes sense to refactor this piece of code and create a custom component - a class that can display addresses for a certain xpub. Also we will add a QR code to this component (`lvqr` module).

Check out the solution - [`main.py`](./main.py)

Now let's continue and work with [PSBT transactions](../5_psbt)