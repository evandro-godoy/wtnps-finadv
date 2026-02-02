"""
FastAPI main application for WTNPS Trade live monitoring.

Provides REST API and WebSocket endpoints for real-time signal visualization.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

from src.api.websocket_manager import WebSocketManager
from src.live.monitor_engine import RealTimeMonitor
from src.events import InferenceSignalEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
monitor_engine: Optional[RealTimeMonitor] = None
ws_manager = WebSocketManager()

# Get template directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = TEMPLATES_DIR / "static"


class StatusResponse(BaseModel):
    """API status response model."""
    running: bool
    ticker: str
    timeframe: str
    last_candle_time: Optional[str]
    uptime_seconds: float


class SignalResponse(BaseModel):
    """Signal data response model."""
    ticker: str
    timestamp: str
    ai_signal: str
    probability: float
    price: float
    indicators: dict
    timeframe: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global monitor_engine
    
    logger.info("Starting FastAPI application...")
    
    # Initialize monitor engine in background
    # Note: Actual monitoring loop should be started separately
    # to allow API to be responsive
    
    yield
    
    # Cleanup
    logger.info("Shutting down FastAPI application...")
    if monitor_engine and monitor_engine.running:
        monitor_engine.stop()


app = FastAPI(
    title="WTNPS Trade Live Monitor API",
    description="REST API and WebSocket for real-time ML signal monitoring",
    version="3.0.0",
    lifespan=lifespan
)

# CORS configuration (allow localhost for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Event handler for inference signals
def handle_inference_signal(event: InferenceSignalEvent):
    """
    Event handler that receives InferenceSignalEvent from MonitorEngine
    and broadcasts via WebSocket.
    """
    signal_data = {
        "type": "signal",
        "data": {
            "ticker": event.ticker,
            "timestamp": event.timestamp.isoformat(),
            "ai_signal": event.ai_signal,
            "probability": event.probability,
            "price": event.price,
            "indicators": event.indicators,
            "timeframe": event.timeframe
        }
    }
    
    # Broadcast to all WebSocket clients
    asyncio.create_task(ws_manager.broadcast(signal_data))


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - serves HTML interface."""
    html_path = TEMPLATES_DIR / "charts_clean.html"
    
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {
            "service": "WTNPS Trade Live Monitor API",
            "version": "3.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "message": "HTML template not found. API endpoints are available."
        }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/status", response_model=StatusResponse, tags=["Monitor"])
async def get_status():
    """Get current monitor engine status."""
    global monitor_engine
    
    if not monitor_engine:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Monitor engine not initialized",
                "running": False
            }
        )
    
    # Calculate uptime
    uptime = 0.0
    if hasattr(monitor_engine, 'start_time'):
        uptime = (datetime.now() - monitor_engine.start_time).total_seconds()
    
    # Get last candle time
    last_candle_time = None
    if monitor_engine.buffer_df is not None and len(monitor_engine.buffer_df) > 0:
        last_candle_time = monitor_engine.buffer_df.index[-1].isoformat()
    
    return StatusResponse(
        running=monitor_engine.running,
        ticker=monitor_engine.ticker,
        timeframe=monitor_engine.timeframe_str,
        last_candle_time=last_candle_time,
        uptime_seconds=uptime
    )


# Signal cache for latest signals
signal_cache: List[dict] = []
MAX_CACHE_SIZE = 100


def cache_signal(event: InferenceSignalEvent):
    """Cache signal for REST API endpoint."""
    signal_data = {
        "ticker": event.ticker,
        "timestamp": event.timestamp.isoformat(),
        "ai_signal": event.ai_signal,
        "probability": event.probability,
        "price": event.price,
        "indicators": event.indicators,
        "timeframe": event.timeframe
    }
    
    signal_cache.append(signal_data)
    
    # Limit cache size
    if len(signal_cache) > MAX_CACHE_SIZE:
        signal_cache.pop(0)


@app.get("/api/signals/latest", response_model=List[SignalResponse], tags=["Signals"])
async def get_latest_signals(limit: int = 100):
    """Get latest cached signals."""
    if limit > MAX_CACHE_SIZE:
        limit = MAX_CACHE_SIZE
    
    return signal_cache[-limit:]


@app.websocket("/ws/live-signals")
async def websocket_live_signals(websocket: WebSocket):
    """
    WebSocket endpoint for real-time signal streaming.
    
    Clients connect here to receive live inference signals as they are generated.
    """
    await ws_manager.connect(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to WTNPS Trade Live Monitor",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and receive client messages (ping/pong)
        while True:
            # Wait for client messages (mainly for ping/pong keep-alive)
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received from client: {data}")
                
                # Echo back for ping/pong
                if data == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error receiving WebSocket data: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        ws_manager.disconnect(websocket)


@app.post("/api/monitor/start", tags=["Monitor"])
async def start_monitor(ticker: str = "WDO$", timeframe: str = "M5"):
    """Start the monitor engine (for testing/manual control)."""
    global monitor_engine
    
    if monitor_engine and monitor_engine.running:
        return JSONResponse(
            status_code=400,
            content={"error": "Monitor already running"}
        )
    
    try:
        monitor_engine = RealTimeMonitor(
            ticker=ticker,
            timeframe_str=timeframe,
            ui_callback=None  # No UI callback for API mode
        )
        
        # Subscribe to inference events
        monitor_engine.event_bus.subscribe("INFERENCE_SIGNAL", handle_inference_signal)
        monitor_engine.event_bus.subscribe("INFERENCE_SIGNAL", cache_signal)
        
        # Start monitor in background task
        asyncio.create_task(run_monitor_loop())
        
        return {
            "status": "started",
            "ticker": ticker,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting monitor: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/api/monitor/stop", tags=["Monitor"])
async def stop_monitor():
    """Stop the monitor engine."""
    global monitor_engine
    
    if not monitor_engine or not monitor_engine.running:
        return JSONResponse(
            status_code=400,
            content={"error": "Monitor not running"}
        )
    
    monitor_engine.stop()
    
    return {
        "status": "stopped",
        "timestamp": datetime.now().isoformat()
    }


async def run_monitor_loop():
    """Background task to run monitor loop."""
    global monitor_engine
    
    if not monitor_engine:
        logger.error("Monitor engine not initialized")
        return
    
    logger.info("Starting monitor loop in background task...")
    
    # Run monitor in thread to avoid blocking
    import threading
    
    def run_in_thread():
        try:
            monitor_engine.start_time = datetime.now()
            monitor_engine.run()
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
    
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
