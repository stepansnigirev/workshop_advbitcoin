# Creating PSBT manually

```py
from rpc import BitcoinCLI
import bech32, hashlib

rpc = BitcoinCLI("specter","TruckWordTrophySolidVintageFieldGalaxyOrphanSeek",port=18443)

# a few examples
rpc.getmininginfo()
rpc.listwallets()

# creating a watch only wallet
rpc.createwallet("testwallet23534534", True)

# wallet rpc, similar to calling bitcoin-cli -rpcwallet=test...
w = rpc.wallet("testwallet23534534")
w.getwalletinfo()

# importing keys
recv_desc = "wpkh([b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq/0/*)"
change_desc = "wpkh([b317ec86/84h/1h/0h]tpubDCKVXMvGq2YRczuCLcfcY8TaxHGjFTuhFrkRGpBk4DXmQeJXM3JAz8ijxTS59PZQBUtiq5wkstpzgvow7A25F4vDbmiAEy3rE4xHcR2XUUq/1/*)"

add_checksum = lambda desc: w.getdescriptorinfo(desc)["descriptor"]
recv_desc = add_checksum(recv_desc)
change_desc = add_checksum(change_desc)

w.importmulti([
    {
        "desc":recv_desc,
        "timestamp":"now",
        "range":[0,1000],
        "internal":False,
        "watchonly":True,
        "keypool":True
    },{
        "desc":change_desc,
        "timestamp":"now",
        "range":[0,1000],
        "internal":True,
        "watchonly":True,
        "keypool":True}
],{"rescan": False})


# getting public keys
addresses = w.deriveaddresses(recv_desc, 10)
print(addresses)
pubkeys = [bytes.fromhex(w.getaddressinfo(addr)["pubkey"])[1:] for addr in addresses]

# creating taproot addresses
taproot_addresses = [bech32.encode("bcrt", 1, pub) for pub in pubkeys]
taproot_addresses

# Get derivation path for address
ver, prog = bech32.decode(addr.split(1)[0], addr)
prog = bytes(prog)

def hash160(data):
    return hashlib.new("ripemd160",
                       hashlib.sha256(data).digest()
                      ).digest()

address_candidates = [
    bech32.encode("bcrt", 0, hash160(b'\x02'+prog)),
    bech32.encode("bcrt", 0, hash160(b'\x03'+prog))
]
addr_info = [w.getaddressinfo(addr) for addr in address_candidates]
result = [info["hdkeypath"] for info in addr_info if "hdkeypath" in info][0]

```