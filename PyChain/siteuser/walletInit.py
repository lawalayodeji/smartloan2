
import binascii
import Crypto.Random
# from Crypto.Hash import SHA
from Crypto.PublicKey import RSA


def walletInitGen():
    random_gen = Crypto.Random.new().read
    pr_key = RSA.generate(1024, random_gen)
    pub_key = pr_key.publickey()

    private_key = binascii.hexlify(pr_key.exportKey(format='DER')).decode('ascii')
    public_key = binascii.hexlify(pub_key.exportKey(format='DER')).decode('ascii')

    return private_key, public_key
