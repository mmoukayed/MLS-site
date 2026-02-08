def university_email_validator(email):
    if not email.endswith("@rit.edu") or email.endswith("@g.rit.edu"):
        raise ValueError("Only university email allowed")
