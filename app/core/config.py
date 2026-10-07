import os
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("MLAPI_API_KEY")
MODEL    = os.getenv("MLAPI_MODEL")
BASE_URL = os.getenv("MLAPI_BASE_URL")
if not API_KEY:
    raise RuntimeError("MLAPI_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요.")
