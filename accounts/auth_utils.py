from django.core.signing import TimestampSigner

signer = TimestampSigner()

def generate_magic_token(email):
    return signer.sign(email)

def verify_magic_token(token, max_age=300):
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None