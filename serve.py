import os
import sys
from waitress import serve
from app import app
import database as db

if __name__ == "__main__":
    # Ensure database is initialized
    db.init_db()
    
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 60)
    print(f"🚀 JUSTBEFIT Gym Management Server Starting")
    print(f"📍 Local access: http://localhost:{port}")
    print(f"🌐 Network access: http://127.0.0.1:{port}")
    print(f"⚙️  Powered by Waitress Production WSGI Server")
    print("=" * 60)
    
    serve(app, host=host, port=port, threads=6)
