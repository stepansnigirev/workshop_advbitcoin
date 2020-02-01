import pyb
import os
import hashlib
from binascii import hexlify

from bitcoin import bip39, bip32, script
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

####################################
#                                  #
#    address generation - part 3   #
#                                  #
####################################

xpub_bip44 = root_key.derive("m/44h/1h/0h").to_public()
# version parameter is optional - by default it uses mainnet xpub.
print("\nLegacy xpub:", xpub_bip44.to_base58(version=network["xpub"]))
print("Legacy addresses:")
for i in range(5):
    # m/0/i is used for receiving addresses and m/1/i for change addresses
    # derive function also accepts lists of indexes
    pub = xpub_bip44.derive([0, i])
    # get p2pkh script
    sc = script.p2pkh(pub)
    print("Address %i: %s" % (i, sc.address(network)))

xpub_bip84 = root_key.derive("m/84h/1h/0h").to_public()
print("\nSegwit zpub:", xpub_bip84.to_base58(version=network["zpub"]))
print("Segwit addresses:")
for i in range(5):
    pub = xpub_bip44.derive([0, i])
    # get p2wsh script
    sc = script.p2wpkh(pub)
    print("Address %i: %s" % (i, sc.address(network)))

xpub_bip49 = root_key.derive("m/49h/1h/0h").to_public()
print("\nNested Segwit ypub:", xpub_bip49.to_base58(version=network["ypub"]))
print("Nested segwit addresses:")
for i in range(5):
    pub = xpub_bip44.derive([0, i])
    # get p2sh(p2wpkh) script
    sc = script.p2sh(script.p2wpkh(pub))
    print("Address %i: %s" % (i, sc.address(network)))
