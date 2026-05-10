# gen_token.py
from app.downloads import generate_download_token
token = generate_download_token(1)
print(f"http://127.0.0.1:8000/download/ebook?token={token}")