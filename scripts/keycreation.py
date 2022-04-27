from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

#Creating SSH Keys
key = rsa.generate_private_key(
	public_exponent=65537,
	key_size=4096
)

private_key = key.private_bytes(
    crypto_serialization.Encoding.PEM,
    crypto_serialization.PrivateFormat.PKCS8,
    crypto_serialization.NoEncryption()
)

public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH
)

private_key_file = open("build\\ecscproxy\\id_rsa", "w")
private_key_file.write(private_key.decode())
private_key_file.close()

public_key_file = open("build\\ecscproxy\\id_rsa.pub", "w")
public_key_file.write(public_key.decode())
public_key_file.close()

public_key_file = open("build\\ecscproxy\\authorized_keys", "w")
public_key_file.write(public_key.decode())
public_key_file.close()