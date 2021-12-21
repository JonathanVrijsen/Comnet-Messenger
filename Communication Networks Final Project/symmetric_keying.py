import hashlib

from cryptography.fernet import Fernet


def hash_string(input_string):
    pb = bytes(input_string, 'utf-8')
    hash = hashlib.sha1(pb)
    return hash.hexdigest()


def symm_encrypt(msg, key):
    cipher = Fernet(key)
    return cipher.encrypt(msg)


def symm_decrypt(msg, key):
    cipher = Fernet(key)
    return cipher.decrypt(msg)


def str_to_symmkey(sym_key_str):
    if sym_key_str[0]=='b' and sym_key_str[1]=='\'' and sym_key_str[len(sym_key_str)-1]=='\'':
        sym_key_str = sym_key_str[2:len(sym_key_str) - 1]
    return bytes(sym_key_str, "utf-8")
