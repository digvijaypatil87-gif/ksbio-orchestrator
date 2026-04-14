from passlib.context import CryptContext

passlibctx = CryptContext(
    schemes=["pbkdf2_sha256", "argon2"],
)

password = "KsbioAdmin2026"
hashed = passlibctx.hash(password)
print(f"Hash: {hashed}")
