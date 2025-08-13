"""
ADPTX Legal AI API Server - FIXED VERSION

A FastAPI-based server providing legal research and analysis capabilities
using AI agents for Indian law research, case analysis, and legal insights.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from fastapi import UploadFile, File, Form
import logging
import time
import os
import asyncio
from datetime import datetime, timedelta
import json
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
import tempfile

# ============================================================================
# LOGGING CONFIGURATION (SIMPLIFIED)
# ============================================================================

# Simple console logging only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL VARIABLES AND UTILITIES
# ============================================================================

# System statistics tracking
system_metrics = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'average_response_time': 0.0,
    'feature_usage': {
        'legal_research': 0,
        'pdf_analysis': 0,
        'pdf_qa': 0
    },
    'last_request_time': None,
    'peak_concurrent_requests': 0,
    'current_concurrent_requests': 0
}

# Session management
active_sessions = {}
session_timeout = timedelta(hours=2)

# Global variables for AI systems
legal_strategist = None
LEGAL_RESEARCH_AVAILABLE = False

def update_metrics(result: Dict[str, Any], execution_time: float):
    """Update system metrics"""
    system_metrics['total_requests'] += 1
    system_metrics['last_request_time'] = datetime.now()
    
    if result.get('status') == 'success':
        system_metrics['successful_requests'] += 1
    else:
        system_metrics['failed_requests'] += 1
    
    # Update average response time
    current_avg = system_metrics['average_response_time']
    total_successful = system_metrics['successful_requests']
    system_metrics['average_response_time'] = (
        (current_avg * (total_successful - 1) + execution_time) / total_successful
    ) if total_successful > 0 else execution_time

def get_uptime() -> str:
    """Get system uptime as string"""
    uptime = datetime.now() - system_metrics['start_time']
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def validate_session(session_id: str) -> bool:
    """Validate if session is still active"""
    if session_id not in active_sessions:
        return False
    
    session_data = active_sessions[session_id]
    if datetime.now() - session_data['created'] > session_timeout:
        del active_sessions[session_id]
        return False
    
    return True

def create_session() -> str:
    """Create a new session"""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        'created': datetime.now(),
        'requests': 0
    }
    return session_id

async def cleanup_expired_sessions():
    """Clean up expired sessions"""
    current_time = datetime.now()
    expired_sessions = [
        session_id for session_id, session_data in active_sessions.items()
        if current_time - session_data['created'] > session_timeout
    ]
    
    for session_id in expired_sessions:
        del active_sessions[session_id]
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

# ============================================================================
# IMPORT AI SYSTEMS (WITH BETTER ERROR HANDLING)
# ============================================================================

def initialize_ai_systems():
    """Initialize AI systems with proper error handling"""
    global legal_strategist, LEGAL_RESEARCH_AVAILABLE
    
    # Check required environment variables
    required_env_vars = ["GROQ_API_KEY", "INDIAN_KANOON_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {missing_vars}")
        logger.warning("Please set these in your Choreo environment configuration")
        logger.warning("Continuing with limited functionality...")
        # Don't return, continue with limited functionality
    
    logger.info("All required environment variables are set")
    
    # Import legal research system
    try:
        from orchestrator import LegalStrategist
        legal_strategist = LegalStrategist()
        LEGAL_RESEARCH_AVAILABLE = True
        logger.info("Legal research system initialized successfully")
    except ImportError as e:
        logger.warning(f"Legal research system not available: {e}")
        LEGAL_RESEARCH_AVAILABLE = False
    except Exception as e:
        logger.error(f"Failed to initialize legal research system: {e}")
        LEGAL_RESEARCH_AVAILABLE = False
    
    # Set default status if API keys are missing
    if missing_vars:
        LEGAL_RESEARCH_AVAILABLE = False

# ============================================================================
# LIFESPAN MANAGER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ADPTX Legal AI API Server...")
    
    # Log environment variable status
    logger.info(f"GROQ_API_KEY: {'✅ Set' if os.getenv('GROQ_API_KEY') else '❌ Missing'}")
    logger.info(f"INDIAN_KANOON_API_KEY: {'✅ Set' if os.getenv('INDIAN_KANOON_API_KEY') else '❌ Missing'}")
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("files", exist_ok=True)
    
    # Initialize AI systems
    initialize_ai_systems()
    
    # Start background task for session cleanup
    cleanup_task = asyncio.create_task(session_cleanup_task())
    
    yield
    
    # Shutdown
    logger.info("Shutting down ADPTX Legal AI API Server...")
    
    # Cancel background task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    # Clear all sessions
    active_sessions.clear()

async def session_cleanup_task():
    """Background task to clean up expired sessions"""
    while True:
        try:
            await cleanup_expired_sessions()
            await asyncio.sleep(300)  # Run every 5 minutes
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in session cleanup task: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

# ============================================================================
# FASTAPI APP CREATION
# ============================================================================

# Create FastAPI application
app = FastAPI(
    title="ADPTX Legal AI API",
    description="AI-powered legal research and analysis system for Indian law",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:3000",
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174", 
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        # Choreo frontend domains
        "https://*.choreoapps.dev",
        "https://*.choreoapis.dev",
        # Allow all origins in production (you can restrict this later)
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User's legal research query")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation continuity")

class ChatResponse(BaseModel):
    """Response model for chat messages"""
    status: str = Field(..., description="Response status (success/error)")
    message: str = Field(..., description="Response message")
    data: Optional[str] = Field(None, description="Legal research results")
    error: Optional[str] = Field(None, description="Error message if any")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_question: Optional[str] = Field(None, description="The user's original question")



class SystemStatus(BaseModel):
    """System status response model"""
    status: str = Field(..., description="System status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    uptime: str = Field(..., description="System uptime")
    statistics: Dict[str, Any] = Field(..., description="System statistics")
    features: List[str] = Field(..., description="Available features")

# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================

async def process_legal_research(query: str, user_id: str = None, session_id: str = None) -> Dict[str, Any]:
    """Process legal research query"""
    try:
        if not LEGAL_RESEARCH_AVAILABLE or not legal_strategist:
            return {
                'status': 'error',
                'error': 'Legal research system not available. Please check if ai_systems.orchestrator is properly installed.'
            }
    
        logger.info(f"Processing legal research query: {query[:100]}...")
        
        # Run legal research with session_id
        result = legal_strategist.run_with_monitoring(query, session_id)
        
        logger.info(f"Legal research completed with status: {result.get('status', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in legal research processing: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }



# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ADPTX Legal AI API Server",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
        "features": {
            "legal_research": LEGAL_RESEARCH_AVAILABLE,
            "pdf_analysis": LEGAL_RESEARCH_AVAILABLE,  # Depends on legal research
            "pdf_qa": LEGAL_RESEARCH_AVAILABLE  # Depends on legal research
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Check environment variables
    env_status = {
        "GROQ_API_KEY": "✅ Set" if os.getenv("GROQ_API_KEY") else "❌ Missing",
        "INDIAN_KANOON_API_KEY": "✅ Set" if os.getenv("INDIAN_KANOON_API_KEY") else "❌ Missing"
    }
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": get_uptime(),
        "environment": env_status,
        "features": {
            "legal_research": LEGAL_RESEARCH_AVAILABLE,
            "pdf_analysis": LEGAL_RESEARCH_AVAILABLE,
            "pdf_qa": LEGAL_RESEARCH_AVAILABLE
        },
        "system_metrics": {
            "total_requests": system_metrics['total_requests'],
            "successful_requests": system_metrics['successful_requests'],
            "failed_requests": system_metrics['failed_requests'],
            "average_response_time": f"{system_metrics['average_response_time']:.3f}s"
        }
    }
    
    # Check if core systems are available
    warnings = []
    if not LEGAL_RESEARCH_AVAILABLE:
        warnings.append("Legal research system not available")
        health_status["status"] = "degraded"
    
    if warnings:
        health_status["warnings"] = warnings
    
    return health_status

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Main chat endpoint for legal research"""
    start_time = time.time()
    
    try:
        # Validate session if provided
        session_id = chat_request.session_id
        if session_id and not validate_session(session_id):
            session_id = create_session()
        
        if not session_id:
            session_id = create_session()
        
        # Process the request
        result = await process_legal_research(chat_request.message, chat_request.user_id, session_id)
        
        execution_time = time.time() - start_time
        update_metrics(result, execution_time)
        system_metrics['feature_usage']['legal_research'] += 1
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]['requests'] += 1
        
        return ChatResponse(
            status=result.get('status', 'error'),
            message=result.get('content', '') if result.get('status') == 'success' else result.get('error', 'Unknown error'),
            data=result.get('content') if result.get('status') == 'success' else None,
            error=result.get('error') if result.get('status') == 'error' else None,
            execution_time=execution_time,
            session_id=session_id,
            user_question=chat_request.message
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        execution_time = time.time() - start_time
        update_metrics({'status': 'error'}, execution_time)
        
        return ChatResponse(
            status="error",
            message="Internal server error",
            error=str(e),
            execution_time=execution_time
        )

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...), 
    user_id: str = Form(...)
):
    """Simple file upload endpoint - FIXED VERSION"""
    try:
        # Validate file
        if not file.filename:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "error": "No file provided"}
            )
        
        # Create upload directory
        upload_dir = Path("files")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"file_{user_id}_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Read file content safely
        try:
            contents = await file.read()
            file_size = len(contents)
            
            # Write file safely
            with open(file_path, 'wb') as f:
                f.write(contents)
                
        except Exception as e:
            logger.error(f"Error reading/saving file: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": f"Failed to process file: {str(e)}"}
            )
        
        logger.info(f"File uploaded successfully: {file_path} (size: {file_size} bytes)")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "file_path": str(file_path),
                "file_size": file_size
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in upload: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": f"Upload failed: {str(e)}"}
        )

@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    """Upload and process a PDF document with AI analysis - FIXED VERSION"""
    try:
        # Check AI system availability
        if not LEGAL_RESEARCH_AVAILABLE or not legal_strategist:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "error": "AI system not available"}
            )
        
        # Validate file
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "error": "Only PDF files are supported"}
            )
        
        # Create upload directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        # Read and save file safely
        try:
            content = await file.read()
            file_size = len(content)
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
                
        except Exception as e:
            logger.error(f"Error reading/saving PDF: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": f"Failed to process PDF: {str(e)}"}
            )
        
        logger.info(f"PDF uploaded: {file_path} (size: {file_size} bytes)")
        
        # Validate session
        if session_id and not validate_session(session_id):
            session_id = create_session()
        if not session_id:
            session_id = create_session()
        
        # Process PDF with orchestrator
        try:
            query = f"upload and process PDF file {file_path}"
            result = legal_strategist.run_with_monitoring(query, session_id)
            
            # Update metrics
            system_metrics['feature_usage']['pdf_analysis'] += 1
            
            if result.get("status") == "success":
                # Clean up uploaded file after processing
                try:
                    os.unlink(file_path)
                    logger.info(f"Cleaned up PDF: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup PDF {file_path}: {e}")
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "document_id": result.get("pdf_metadata", {}).get("document_id"),
                        "message": result.get("content", "PDF processed successfully"),
                        "chunks_count": result.get("pdf_metadata", {}).get("chunks_count", 0),
                        "session_id": session_id
                    }
                )
            else:
                # Clean up on failure
                try:
                    os.unlink(file_path)
                except:
                    pass
                    
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error", 
                        "error": result.get("error", "PDF processing failed")
                    }
                )
                
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            # Clean up on error
            try:
                os.unlink(file_path)
            except:
                pass
                
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": f"PDF processing error: {str(e)}"}
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in PDF upload: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": f"Upload failed: {str(e)}"}
        )



@app.get("/api/status", response_model=SystemStatus)
async def system_status():
    """Get detailed system status"""
    # Get legal research statistics if available
    legal_stats = {}
    if LEGAL_RESEARCH_AVAILABLE and legal_strategist:
        try:
            legal_stats = legal_strategist.get_statistics() if hasattr(legal_strategist, 'get_statistics') else {}
        except Exception as e:
            logger.error(f"Error getting legal research statistics: {e}")
    
    features = []
    if LEGAL_RESEARCH_AVAILABLE:
        features.extend(["legal_research", "pdf_analysis", "pdf_qa"])
    
    status = {
        "status": "running",
        "service": "ADPTX Legal AI API",
        "version": "1.0.0",
        "uptime": get_uptime(),
        "statistics": {
            "api_requests": system_metrics,
            "legal_research": legal_stats,
            "active_sessions": len(active_sessions)
        },
        "features": features
    }
    
    return SystemStatus(**status)

@app.post("/api/analyze-pdf")
async def analyze_pdf_endpoint(
    file: UploadFile = File(...),
    message: str = Form(...),
    user_id: str = Form(...)
):
    """Analyze uploaded PDF with custom message - FIXED VERSION"""
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "error": "Only PDF files are supported"}
            )
        
        # Check if AI system is available
        if not LEGAL_RESEARCH_AVAILABLE or not legal_strategist:
            return JSONResponse(
                status_code=503,
                content={"status": "error", "error": "Legal AI system not available"}
            )
        
        # Create upload directory
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Save uploaded file with unique name
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        try:
            content = await file.read()
            file_size = len(content)
            
            with open(file_path, "wb") as buffer:
                buffer.write(content)
                
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": f"Failed to save PDF: {str(e)}"}
            )
        
        logger.info(f"PDF uploaded for analysis: {file_path} (size: {file_size} bytes)")
        
        # Create or validate session
        session_id = create_session()
        
        try:
            # Process the PDF with the user's message
            query = f"{message}. Process PDF file: {file_path}"
            result = legal_strategist.run_with_monitoring(query, session_id)
            
            execution_time = time.time() - start_time
            
            # Update metrics
            update_metrics(result, execution_time)
            system_metrics['feature_usage']['pdf_analysis'] += 1
            
            # Clean up uploaded file
            try:
                os.unlink(file_path)
                logger.info(f"Cleaned up PDF: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup PDF {file_path}: {e}")
            
            if result.get("status") == "success":
                return JSONResponse(
                    status_code=200,
                    content={
                        "status": "success",
                        "message": "PDF analyzed successfully",
                        "analysis": result.get("content"),
                        "user_message": message,
                        "filename": file.filename,
                        "execution_time": execution_time,
                        "session_id": session_id
                    }
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "error": result.get("error", "PDF analysis failed"),
                        "user_message": message,
                        "filename": file.filename,
                        "execution_time": execution_time
                    }
                )
                
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            # Clean up on error
            try:
                os.unlink(file_path)
            except:
                pass
                
            return JSONResponse(
                status_code=500,
                content={"status": "error", "error": f"PDF analysis error: {str(e)}"}
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in PDF analysis: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": f"Server error: {str(e)}"}
        )

@app.post("/api/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Simple test upload endpoint to debug file handling"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file info without processing content
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": 0
        }
        
        # Try to read file size
        content = await file.read()
        file_info["size"] = len(content)
        
        # Reset file pointer
        await file.seek(0)
    
        return {
            "status": "success",
            "message": "File received successfully",
            "file_info": file_info
        }
        
    except Exception as e:
        logger.error(f"Test upload error: {e}")
        return {
            "status": "error", 
            "error": str(e)
        }
    """Clean up uploaded file"""
    try:
        if file_path.exists():
            os.unlink(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup file {file_path}: {e}")
    """Get detailed system statistics"""
    stats = {
        "api_metrics": system_metrics,
        "legal_research": {},
        "sessions": {
            "active_sessions": len(active_sessions),
            "session_timeout_hours": session_timeout.total_seconds() / 3600
        },
        "features_available": {
            "legal_research": LEGAL_RESEARCH_AVAILABLE,
            "document_analysis": DOCUMENT_ANALYSIS_AVAILABLE
        }
    }
    
    if LEGAL_RESEARCH_AVAILABLE and legal_strategist:
        try:
            if hasattr(legal_strategist, 'get_statistics'):
                stats["legal_research"] = legal_strategist.get_statistics()
        except Exception as e:
            logger.error(f"Error getting legal research statistics: {e}")
    
    return stats

# ============================================================================
# ERROR HANDLERS
# ============================================================================

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle validation errors without trying to decode binary data"""
    logger.error(f"Validation error on {request.url}: {exc}")
    
    # Check if this is a file upload error
    if "multipart" in str(request.headers.get("content-type", "")):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Invalid file upload format. Ensure you're uploading a valid file with proper form data.",
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "detail": "File upload validation failed"
            }
        )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request validation failed",
            "status": "error", 
            "timestamp": datetime.now().isoformat(),
            "detail": str(exc)
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable (for Choreo deployment)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )