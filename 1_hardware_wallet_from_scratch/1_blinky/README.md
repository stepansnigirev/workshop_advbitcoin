# Get familiar with MicroPython REPL

You did the setup and connected to the board, right?

Then you see interactive console now, something like:

```
MicroPython v1.10-1162-gb827a8b5e on 2020-01-22; F469DISC with STM32F469
Type "help()" for more information.
>>> 
```

And you can type here. Type `help('modules')` and you will see all modules available on the board.

To reset the board press `Ctrl+D` or the black button on the back.
- `Ctrl+D` - soft reset,
- black button - hard reset (you can also use `pyb.hard_reset()`)

## Blinking with LEDs

Let's start with something simple, blinking with LEDs. LED class is available in the `pyb` module, so let's just blink with all 4 leds:

```py
import pyb
leds = [pyb.LED(i) for i in range(1,5)] # LED(1)...LED(4)
for led in leds:
    led.toggle() # .on() or .off() also work 
```

Yey! Works! Now let's generate a random byte sequence - we will need it for our private keys. 

## Generating some entropy

MicroPython is trying to mimic normal python, so even though there is no OS we still have an `os` module, and there we have `os.urandom(n)` function that generates a sequence of random bytes. Under the hood this function talks to TRNG in the MCU and gets `n` random bytes from it.

```py
import os
import hashlib
# get a lot of random bytes, hash, get 16 bytes out
entropy = hashlib.sha256(os.urandom(2048)).digest()[:16]
print(entropy)
```

If we want to get more entropy - we can mix together other sources, for example readings from ADC (analog-to-digital converter). 

## Excersize:

- Add some entropy from ADC (hint: `pyb.ADC("A0")`)
- Save entropy as a binary file `/flash/entropy`
- Check if you can read entropy from file - use it, otherwise - generate and save

Hint: `with open("/flash/entropy", "rb") as f:` should work as normal.

## Solution

Here is the final [`main.py`](./main.py) file. 

Copy it to the board and reset it (`Ctrl+D` or press the black button on the back).

## Next

Next we will use this entropy to generate the recovery phrase and master keys.

Continue to [2 - HD keys](../2_hdkeys)