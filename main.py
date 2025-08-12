"""
ADPTX Legal AI API Server - Root Entry Point

This file serves as the entry point to run the backend server.
It simply imports and runs the main server from the backend directory.
"""

import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Change to the backend directory
os.chdir(backend_dir)

# Import and run the main server
if __name__ == "__main__":
    from main import app
    import uvicorn
    
    # Get port from environment variable (for Choreo deployment)
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
