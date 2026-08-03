import uvicorn
from zara_ai_server.config import get_settings
from zara_ai_server.main import app

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=8443, log_level="info")
