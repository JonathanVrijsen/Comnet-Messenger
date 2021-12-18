import rsa

def generateKeys():
    return rsa.newkeys(1024)

def encrypt(content, key):
    return rsa.encrypt(content.encode('ascii'), key)

def decrypt(ciphercontent, key):
    try:
        return rsa.decrypt(ciphercontent, key).decode('ascii')
    except:
        return False

def signSHA1(content, key):
    return rsa.sign(content.encode('ascii'), key, 'SHA-1')

def verifySHA1(content, signature, key):
    try:
        return rsa.verify(content.encode('ascii'), signature, key) == 'SHA-1'
    except:
        return False

(pubKey, privKey)=generateKeys()

content=input('Enter a message:')
ciphercontent=encrypt(content, pubKey)

signature = signSHA1(content, privKey)

#at the other end
plaintext=decrypt(ciphercontent, privKey)
print(f'Cipher text: {ciphercontent}')
print(f'Signature: {signature}')

if plaintext:
    print(f'Plain text: {plaintext}')

if verifySHA1(plaintext, signature, pubKey):
    print('Signature verified')
else:
    print('Signature not verified')