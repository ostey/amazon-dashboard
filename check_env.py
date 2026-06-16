import os
from dotenv import load_dotenv

load_dotenv()

print("dotenv loaded =", True)
print("CLIENT_ID =", os.getenv("SP_API_CLIENT_ID"))
print("CLIENT_SECRET =", os.getenv("SP_API_CLIENT_SECRET"))
print("REFRESH_TOKEN =", os.getenv("SP_API_REFRESH_TOKEN"))