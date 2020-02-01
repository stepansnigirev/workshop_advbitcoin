import pyb
import os
import hashlib
from binascii import hexlify

from bitcoin import bip39, bip32
from bitcoin.networks import NETWORKS

####################################
#                                  #
#  entropy generation from part 1  #
#                                  #
####################################

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

####################################
#                                  #
#      key generation - part 2     #
#                                  #
####################################

################# BIP-39 #####################

phrase = bip39.mnemonic_from_bytes(entropy)
print("Your recovery phrase:\n%s\n" % phrase)

# uncomment this line to make invalid mnemonic:
# phrase += " satoshi"

# you can check if recovery phrase is valid or not:
if not bip39.mnemonic_is_valid(phrase):
    raise ValueError("Meh... Typo in the recovery?")

# convert mnemonic and password to bip-32 seed
seed = bip39.mnemonic_to_seed(phrase, password="mysecurepassword")
print("Seed:", hexlify(seed).decode())

################# BIP-32 #####################

# we will use signet:
network = NETWORKS["signet"]

# create HDKey from 64-byte seed
root_key = bip32.HDKey.from_seed(seed)
# generate an account child key:
# purpose: 84h - BIP-84
# coin type: 1h - Testnet
# account: 0h - first account
account = root_key.derive("m/84h/1h/0h")
# convert HD private key to HD public key
account_pub = account.to_public()
# for Bitcoin Core: pure BIP-32 serialization
print("Your xpub:", account_pub.to_base58(version=network["xpub"]))
# for Electrum and others who cares about SLIP-0132
# used for bip-84 by many wallets
print("Your zpub:", account_pub.to_base58(version=network["zpub"]))

############### Bitcoin Core ###################

fingerprint = root_key.child(0).fingerprint
print("Your xpub for Bitcoin Core:")
print("[%s/84h/1h/0h]%s" % (
    hexlify(fingerprint).decode(), 
    account_pub.to_base58(version=network["xpub"]))
)
