# Save as check_fingerprint.py
import base64
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat

pem = Path(r"C:\Users\Manisha\.snowflake\rsa_key.p8").read_bytes()
key = load_pem_private_key(pem, password=None)

pub_der = key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(pub_der).digest()).decode()
print(f"Local key fingerprint: {fingerprint}")