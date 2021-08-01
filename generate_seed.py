import random, binascii
from nano25519 import ed25519_oop as ed25519
from jcnanolib import nano

full_wallet_seed = hex(random.SystemRandom().getrandbits(256))
wallet_seed = full_wallet_seed[2:].upper()
print("Wallet Seed (make a copy of this in a safe place!): {}".format(wallet_seed))

priv_key, pub_key = nano.seed_account(str(wallet_seed), 0)
public_key = str(binascii.hexlify(pub_key), 'ascii')
print("Public Key: ", str(public_key))

account = nano.account_xrb(str(public_key))

print("XRB Address: {}".format(account))
