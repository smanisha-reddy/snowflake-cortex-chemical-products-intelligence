from pathlib import Path
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    PrivateFormat,
    NoEncryption,
)
import snowflake.connector

# Local private key path - do not commit the actual key file
pem = Path(r"<SNOWFLAKE_PRIVATE_KEY_PATH>").read_bytes()

key = load_pem_private_key(pem, password=None)

private_key_der = key.private_bytes(
    Encoding.DER,
    PrivateFormat.PKCS8,
    NoEncryption(),
)

conn = snowflake.connector.connect(
    account="<SNOWFLAKE_ACCOUNT>",
    user="<SNOWFLAKE_USER>",
    authenticator="snowflake_jwt",
    private_key=private_key_der,
    role="<SNOWFLAKE_ROLE>",
    warehouse="<SNOWFLAKE_WAREHOUSE>",
    database="<SNOWFLAKE_DATABASE>",
    schema="<SNOWFLAKE_SCHEMA>",
)

print(conn.cursor().execute("SELECT CURRENT_USER(), CURRENT_ROLE()").fetchone())

conn.close()
