from cryptography.fernet import Fernet

def symmEncrypt(msg, key):
    cipher = Fernet(key)
    return cipher.encrypt(msg)

def symmDecrypt(msg, key):
    cipher = Fernet(key)
    return cipher.decrypt(msg)