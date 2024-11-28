import random

def generate_random_account():
    email = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456789', k=10)) + '@example.com'
    password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz123456789', k=10))
    return email, password