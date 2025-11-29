import hashlib
import os
import base64
def hash_password(password):
    salt = os.urandom(16)  # Generate a 16-byte random salt
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, hashed

def verify_password(password_to_check: str, stored_salt_b64: str, stored_hash_b64: str) -> bool:
    """Verify a user's password against the stored hash and salt."""
    try:
        stored_salt = base64.b64decode(stored_salt_b64)
        stored_hash = base64.b64decode(stored_hash_b64)
    except Exception:
        return False  # if decoding fails

    # Recreate hash using same method as registration
    new_hash = hashlib.pbkdf2_hmac('sha256', password_to_check.encode(), stored_salt, 100_000)
    return new_hash == stored_hash
