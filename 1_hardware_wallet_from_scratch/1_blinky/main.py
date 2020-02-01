import pyb
import os
import hashlib
from binascii import hexlify

ENTROPY_FILE = "/flash/entropy"

try:
    with open(ENTROPY_FILE, "rb") as f:
        entropy = f.read()
    print("Entropy loaded from file")
except:
    print("Generating some entropy")
    trng_entropy = os.urandom(256) # why not 256?
    adc = pyb.ADC("A0")
    adc_entropy = bytes([adc.read()%256 for i in range(200)])
    entropy = hashlib.sha256(trng_entropy+adc_entropy).digest()[:16]
    print("Final entropy:", hexlify(entropy).decode())
    with open(ENTROPY_FILE, "wb") as f:
        f.write(entropy)
    print("Entropy saved")

