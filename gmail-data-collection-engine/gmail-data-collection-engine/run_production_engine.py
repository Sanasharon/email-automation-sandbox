"""
Production SaaS Engine Entry Point.
Launches FastAPI backend server on port 8000 with persistent APScheduler background polling and real-time SSE stream support.
"""
import sys
import os
import uvicorn

# Ensure project root is in python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    print("=" * 80)
    print("      LAUNCHING UTSERVIO GMAIL AUTOMATION ENGINE (PRODUCTION MODE)")
    print("=" * 80)
    print("  - API Host         : http://localhost:8000")
    print("  - Swagger Docs     : http://localhost:8000/docs")
    print("  - Real-Time SSE    : http://localhost:8000/api/v1/events/stream")
    print("  - Scheduler Status : http://localhost:8000/api/v1/system/status")
    print("=" * 80)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
