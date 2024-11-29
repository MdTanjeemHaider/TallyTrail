import random
import string

def generate_random_account():
    """
    Generates a random email and password for testing purposes.

    Returns:
        tuple: A tuple containing a randomly generated email and password.
    """
    email_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{email_prefix}@example.com"  # Append domain to generate email
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # Alphanumeric password
    return email, password