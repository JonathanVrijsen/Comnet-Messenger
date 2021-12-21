import asymmetric_keying

(pubKeySender, privKeySender) = asymmetric_keying.generate_keys()
(pubKeyReceiver, privKeyReceiver) = asymmetric_keying.generate_keys()

content = input('Enter a message:')
cipher_content = asymmetric_keying.encrypt(content.encode('ascii'), pubKeyReceiver)

signature = asymmetric_keying.sign_sha1(content.encode('ascii'), privKeySender)

# at the other end
plaintext = asymmetric_keying.decrypt(cipher_content, privKeyReceiver)
print(f'Cipher text: {cipher_content}')
print(f'Signature: {signature}')

if plaintext:
    print(f'Plain text: {plaintext}')

if asymmetric_keying.verify_sha1(plaintext, signature, pubKeySender):
    print('Signature verified')
else:
    print('Signature not verified')


msg=input('Enter a message:')

cipher_msg=asymmetric_keying.rsa_sendable(msg, privKeySender, pubKeyReceiver)
print(cipher_msg)

msg=asymmetric_keying.rsa_receive(cipher_msg, pubKeySender, privKeyReceiver)
print(msg)
