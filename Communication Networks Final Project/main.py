import asymmetricKeying

(pubKeySender, privKeySender) = asymmetricKeying.generateKeys()
(pubKeyReceiver, privKeyReceiver) = asymmetricKeying.generateKeys()

content = input('Enter a message:')
ciphercontent = asymmetricKeying.encrypt(content.encode('ascii'), pubKeyReceiver)

signature = asymmetricKeying.signSHA1(content.encode('ascii'), privKeySender)

# at the other end
plaintext = asymmetricKeying.decrypt(ciphercontent, privKeyReceiver)
print(f'Cipher text: {ciphercontent}')
print(f'Signature: {signature}')

if plaintext:
    print(f'Plain text: {plaintext}')

if asymmetricKeying.verifySHA1(plaintext, signature, pubKeySender):
    print('Signature verified')
else:
    print('Signature not verified')


msg=input('Enter a message:')

cipher_msg=asymmetricKeying.rsa_sendable(msg, privKeySender, pubKeyReceiver)
print(cipher_msg)

msg=asymmetricKeying.rsa_receive(cipher_msg, pubKeySender, privKeyReceiver)
print(msg)
