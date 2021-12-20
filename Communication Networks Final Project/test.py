from cryptography.fernet import Fernet

# import asymmetricKeying
# from byteStream import ByteStream
# from byteStreamType import ByteStreamType
#
# newSymKey = Fernet.generate_key()
#
# msg_bs = ByteStream(ByteStreamType.symkeyanswer, newSymKey)
#
#
# msgIn = msg_bs.outStream
# byteStreamIn = ByteStream(msgIn)
# Keyserver_symkey = byteStreamIn.content
#
# print(Keyserver_symkey)
# print(type(Keyserver_symkey))

import hashlib

hash_object = hashlib.sha1(b'Hello World')

password = ""
pb = bytes(password, 'utf-8')
x = hashlib.sha1(pb)

pb = bytes(password, 'utf-8')
y = hashlib.sha1(pb)
print(type(hash_object.hexdigest()))
print(y.hexdigest())


