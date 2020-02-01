import pyb
import os
import hashlib
from binascii import hexlify

print("Generating some entropy")
trng_entropy = os.urandom(256) # why not 256?
adc = pyb.ADC("A0")
adc_entropy = bytes([adc.read()%256 for i in range(200)])
entropy = hashlib.sha256(trng_entropy+adc_entropy).digest()[:16]
print("Final entropy:", hexlify(entropy).decode())