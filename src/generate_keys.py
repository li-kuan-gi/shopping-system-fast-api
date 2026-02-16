import json
import time
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def generate_keys():
    # 1. Generate EC Key Pair (P-256)
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    # 2. Serialize Public Key to JWK
    # We use community libraries or manual construction since PyJWT doesn't export JWK gen directly easily
    # But actually, we can use the `jwt` library's potential helpers or `cryptography`
    # Let's construct the JWK manually from the public numbers for maximum compatibility

    numbers = public_key.public_numbers()
    x = numbers.x.to_bytes(32, byteorder="big")
    y = numbers.y.to_bytes(32, byteorder="big")

    # Base64URL encode without padding
    import base64

    def b64_kv(val: bytes) -> str:
        return base64.urlsafe_b64encode(val).rstrip(b"=").decode("utf-8")

    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": b64_kv(x),
        "y": b64_kv(y),
        "alg": "ES256",
        "use": "sig",
        "kid": "local-dev-key",
    }

    # 3. Create a JWT signed with the Private Key
    # We need the private key in PEM format for jwt.encode
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    token_payload = {
        "sub": "local-user-ud-123",  # Subject (User ID)
        "role": "authenticated",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600 * 24 * 30,  # 30 days expiration
        "iat": int(time.time()),
    }

    token = jwt.encode(
        token_payload, pem_private, algorithm="ES256", headers={"kid": "local-dev-key"}
    )

    print("\n--- LOCAL DEVELOPMENT KEYS ---\n")
    print(f"Put this in your .env as JWT_SIGNING_KEY:\n")
    print(json.dumps(jwk))
    print("\n-------------------------------------------------------\n")
    print(f"Use this Token for Authorization header (Bearer <token>):\n")
    print(token)
    print("\n-------------------------------------------------------\n")


if __name__ == "__main__":
    generate_keys()
