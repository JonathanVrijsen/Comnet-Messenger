import hashlib

from cryptography.fernet import Fernet

#not related to symmetric keying. Calculates a SHA-1 has of a given string
#used for instance to hash passwords and create conversation ids
def hash_string(input_string):
    pb = bytes(input_string, 'utf-8') #encode string to bytes
    hash = hashlib.sha1(pb) #perform hash
    return hash.hexdigest()  #return string of hash

#Encrypting and decrypting symmetric keys. Self-explanatory
def symm_encrypt(msg, key):
    cipher = Fernet(key)
    return cipher.encrypt(msg)


def symm_decrypt(msg, key):
    cipher = Fernet(key)
    return cipher.decrypt(msg)

#Re-convert a string of a key to an actual key. Used after transmitting symmetric keys as strings
def str_to_symmkey(sym_key_str):
    # Often they arrive in the form "b'*actual key in bytes*'", thus the first two and lasy characted should be deleted in this case
    if sym_key_str[0]=='b' and sym_key_str[1]=='\'' and sym_key_str[len(sym_key_str)-1]=='\'':
        sym_key_str = sym_key_str[2:len(sym_key_str) - 1]
    return bytes(sym_key_str, "utf-8") #convert string to bytes-like object
