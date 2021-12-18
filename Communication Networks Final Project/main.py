import asymmetricKeying

(pubKeySender, privKeySender)=generateKeys()
(pubKeyReceiver, privKeyReceiver)=generateKeys()

content=input('Enter a message:')
ciphercontent=encrypt(content, pubKeyReceiver)

signature = signSHA1(content, privKeySender)

#at the other end
plaintext=decrypt(ciphercontent, privKeyReceiver)
print(f'Cipher text: {ciphercontent}')
print(f'Signature: {signature}')

if plaintext:
    print(f'Plain text: {plaintext}')

if verifySHA1(plaintext, signature, pubKeySender):
    print('Signature verified')
else:
    print('Signature not verified')