import ecdsa
import binascii
#This generates key pair so that only one ecdsa dependency
def generateKeyPair():
	sender = ecdsa.SigningKey.generate()
	sendervk = sender.get_verifying_key()
	return sender, sendervk
def generateSignature(message):
	sender = ecdsa.SigningKey.generate()
	sendervk = sender.get_verifying_key()
	signature = sendervk.sign(message.encode('utf-8'))
	return signature, sendervk
def signWithPrivateKey(message, sendervk):
	sender = binascii.unhexlify(sendervk.encode('ascii'))
	sender = ecdsa.SigningKey.from_string(sender)
	signature = sender.sign(message.encode('utf-8'))
	return signature

def verifyingExisting(message, sendervk, signature):
	sendervk = binascii.unhexlify(sendervk.encode('ascii'))
	sendervk = ecdsa.VerifyingKey.from_string(sendervk)
	return sendervk.verify(signature, message.encode('utf-8'))
def generateVerifyingKeyPairs():
	message = "Blockchain Technology"
	signature, sendervk = generateSignature(message)
	return verifyingExisting(message, sendervk, signature)

#118b2cc2e99d5219d16a7c02146a93ed0157d718f312f90367c517fb9a422426ec1ce8cbb0f84718be89cc7276bda3cf
#f6924ee5e6a2c513cf8537ab8797139d8a61506374282f52