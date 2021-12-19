import rsa


def generateKeys():
    return rsa.newkeys(1024)


def encrypt(content, key):
    return rsa.encrypt(content, key)


def decrypt(ciphercontent, key):
    try:
        return rsa.decrypt(ciphercontent, key).decode('ascii')
    except:
        return False


def signSHA1(content, key):
    return rsa.sign(content, key, 'SHA-1')


def verifySHA1(content, signature, key):
    try:
        return rsa.verify(content.encode('ascii'), signature, key) == 'SHA-1'
    except:
        return False


def rsa_sendable(msg, privKeySender, pubKeyReceiver): #used by all the piers that need to send any content
    #assuming message is a string
    msg = msg.encode('ascii')

    cipher_msg = encrypt(msg, pubKeyReceiver)
    signature = signSHA1(msg, privKeySender)
    return signature + cipher_msg


def rsa_receive(cipher_msg, pubKeySender, privKeyReceiver):
    signature = cipher_msg[:128] #1024 bits key used, so signature is always 128 bytes
    cipher_msg=cipher_msg[128:]

    msg = decrypt(cipher_msg, privKeyReceiver)

    if verifySHA1(msg, signature, pubKeySender):
        return msg
    else:
        return False


