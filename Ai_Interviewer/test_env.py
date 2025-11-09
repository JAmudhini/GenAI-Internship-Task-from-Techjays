import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Testing Environment Variables")
print("=" * 50)

secret_key = os.getenv('SECRET_KEY')
debug = os.getenv('DEBUG')
gemini_key = os.getenv('GEMINI_API_KEY')

print(f"SECRET_KEY found: {bool(secret_key)}")
print(f"DEBUG found: {bool(debug)}")
print(f"GEMINI_API_KEY found: {bool(gemini_key)}")

if gemini_key:
    print(f"GEMINI_API_KEY starts with: {gemini_key[:10]}...")
else:
    print("❌ GEMINI_API_KEY is NOT set!")
    print("\nPlease add this line to your .env file:")
    print("GEMINI_API_KEY=your-actual-api-key-here")

print("=" * 50)