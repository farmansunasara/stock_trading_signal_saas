"""
Script to generate a secure SECRET_KEY for JWT
Run this and copy the output to your .env file
"""
import secrets

secret_key = secrets.token_urlsafe(32)
print("Generated SECRET_KEY:")
print(secret_key)
print("\nAdd this to your backend/.env file:")
print(f"SECRET_KEY={secret_key}")
