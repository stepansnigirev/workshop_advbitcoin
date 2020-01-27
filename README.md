# Purpose (to be removed)

We'll have two workshops on the Advancing Bitcoin Conference in London:

* One is focussing on curious devs that never worked with hardware. The goal is to guide them through first steps of hardware development and show that they can apply their knowledge for hardware wallets. MicroPython + programming HW from scratch on the devboard. Based on the [youtube series](https://www.youtube.com/playlist?list=PLn2qRQUAAg0z_-R0swVuSsNS9bzRu6oP5).

* The other one is focused on developers, both specter-diy and specter-desktop. Here we want to convince people to contribute to projects. So we need to show them that we are open for their contribution, we have already a reasonably large codebase so it's not that easy to rewrite from scratch but still not mature enough to be scared. We can show that there are still many things to do and we are willing to experiment and integrate new features.

Rough ideas about the flow for the second workshop:
- Setting up hardware wallet and desktop app
- Demo the flow with single key / multisig
  - most people will have just a board without QR scanner, so they will use USB mode
  - we still can show the kit and QR flow
- Overview of the architecture and design choices we made:
  - Security model of the HW
    - Airgap and QR scanner
    - Micropython & libsecp256k1
    - Secure element and the kit
    - Portability
  - Security model of the desktop app:
    - Watch only
    - Multisig focused
    - Privacy focused
    - Avoid npm, frameworks, keep it modular
- Internals of specter-diy
  - keystore module and verification logic
  - wallets and why you need to add them
  - PIN code verification
  - GUI, communication modules
  - config and developer / production mode
  - In depth code inspection: PSBT verification & display
- Internals of specter-desktop
  - ...
- Coin selection
  - Implement in desktop
  - Implement in hardware
  - Testing
- Change index boundaries
  - Implement in hardware
    - save last seen change index to wallet file
    - check the diff & warn if diff > 20
- Mixed inputs
  - Allow mixed inputs
  - Display amounts sent from wallet A and wallet B
- Detect transfer between wallets
  - Change app to include derivation information for other wallets
  - Change wallet to verify
  - Add watch-only wallets - aka Contact List
- Schnorr & Taproot hardware wallet integration with Kalle's signet

For each workshop, we'll create two folders which contains problem and solution in seperated files.
We probably don't have seperated "trainer-notes".

# General info

Testnet & Signet nodes available:

- http(s)://testnet.specterwallet.io
- http(s)://signet.specterwallet.io
- port: 80 for http, 443 for https
- rpcuser: specter
- rpcpassword: TruckWordTrophySolidVintageFieldGalaxyOrphanSeek

# Let's get started

- [Beginner](beginner/README.md)
- [Advanced](advanced/README.md)

# Workshops flow
