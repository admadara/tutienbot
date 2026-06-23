import threading
import asyncio
import os
from web.app import app
import bot

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

if __name__ == "__main__":
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    asyncio.run(bot.main())
