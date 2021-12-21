import hashlib

from cryptography.fernet import Fernet

def hashString(input_string):
    pb = bytes(input_string, 'utf-8')
    hash = hashlib.sha1(pb)
    return hash.hexdigest()

def symmEncrypt(msg, key):
    cipher = Fernet(key)
    return cipher.encrypt(msg)

def symmDecrypt(msg, key):
    cipher = Fernet(key)
    return cipher.decrypt(msg)

def strToSymkey(SymKeyStr):
    SymKeyStr = SymKeyStr[2:len(SymKeyStr)-1]
    return bytes(SymKeyStr, "utf-8")
