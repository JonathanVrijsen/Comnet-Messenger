from base64 import b64decode

import rsa


def generate_keys():
    #generates public and corresponding private key
    return rsa.newkeys(1024)


def encrypt(content, key):
    return rsa.encrypt(content, key)


def decrypt(cipher_content, key):
    try:
        return rsa.decrypt(cipher_content, key).decode('ascii')
    except:
        return False


def sign_sha1(content, key):
    return rsa.sign(content, key, 'SHA-1')


def verify_sha1(content, signature, key):
    try:
        return rsa.verify(content.encode('ascii'), signature, key) == 'SHA-1'
    except:
        return False

#REFERENCE: all functions implemented upon till here are based on a toturial on rsa encryption in Python by Basseltech:
#https://www.youtube.com/watch?v=txz8wYLITGk

def rsa_sendable(msg, priv_key_sender, pub_key_receiver):  # used by all the piers that need to create a secure channel
    # assuming message is a string
    cipher_msg = encrypt(msg, pub_key_receiver)
    signature = sign_sha1(msg, priv_key_sender)
    #concatenation of signature and encrypted message is sent. Signature is always 128 bytes
    return signature + cipher_msg


def rsa_receive(cipher_msg, pub_key_sender, priv_key_receiver):
    signature = cipher_msg[:128]  # 1024 bits key used, so signature is always 128 bytes
    cipher_msg = cipher_msg[128:]

    msg = decrypt(cipher_msg, priv_key_receiver)

    if verify_sha1(msg, signature, pub_key_sender):
        return msg
    else:
        return False
    #returns decrypted message if signature is correct, else False


def string_to_pubkey(pub_key_str):
    #used to convert a string of a public key to its original public or private key. Needed to transmit public keys between nodes
    f, l = pub_key_str.split('(')
    n, e = l.split(',')
    e = e[1:len(e) - 1]
    pub_key = rsa.PublicKey(int(n), int(e))
    return pub_key
