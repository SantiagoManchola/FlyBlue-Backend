import os
from dotenv import load_dotenv

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "flyblue_secret_key_2024")
ALGORITHM = "HS256"