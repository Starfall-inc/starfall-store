import bcrypt


def hash_password(password):
    """Securely hash a password."""
    password_bytes = password.encode('utf-8')  # Encode password
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())  # Hash password
    return hashed_password.decode('utf-8')  # Decode to string for storage


def confirm_password_hash(hashed_password, password):
    """Check if password matches the hashed password."""
    password_bytes = password.encode('utf-8')  # Encode password
    # Ensure hashed_password is a string before encoding
    if isinstance(hashed_password, str):
        hashed_password_bytes = hashed_password.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)  # Verify password


# Example usage
hashed_pw = hash_password("MySecurePassword")
print("Hashed Password:", hashed_pw)

# Confirm password
if confirm_password_hash(hashed_pw, "MySecurePassword"):
    print("✅ Password matches!")
else:
    print("❌ Incorrect password!")
