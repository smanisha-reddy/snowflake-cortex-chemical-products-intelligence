import base64
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PrivateFormat, NoEncryption
import snowflake.connector

pem = Path(r"C:\Users\Manisha\.snowflake\rsa_key.p8").read_bytes()
key = load_pem_private_key(pem, password=None)
private_key_der = key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())

conn = snowflake.connector.connect(
    account="FPIXIZB-MG82313",
    user="MANISHAREDDY23",
    authenticator="snowflake_jwt",
    private_key=private_key_der,
    role="ACCOUNTADMIN",
    warehouse="CORTEX_WH",
    database="CHEM_DB",
    schema="CURATED",
)

print(conn.cursor().execute("SELECT CURRENT_USER()").fetchone())
conn.close()