"""
FastAPI main application for WTNPS Trade live monitoring.

Provides REST API and WebSocket endpoints for real-time signal visualization.
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, Tuple

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path

from src.api.websocket_manager import WebSocketManager
from src.api.routes.chart_data import router as chart_data_router
from src.core.config import settings
from src.live.monitor_engine import RealTimeMonitor
from src.events import InferenceSignalEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
monitor_engine: Optional[RealTimeMonitor] = None
monitor_thread: Optional[threading.Thread] = None
monitor_lock = threading.Lock()
ws_manager = WebSocketManager()

# Get template directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
ROOT_STATIC_DIR = BASE_DIR / "static"
ROOT_STATIC_READY = (ROOT_STATIC_DIR / "css").exists() or (ROOT_STATIC_DIR / "js").exists()
STATIC_DIR = ROOT_STATIC_DIR if ROOT_STATIC_READY else TEMPLATES_DIR / "static"


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


def _read_template(template_name: str) -> Optional[str]:
    html_path = TEMPLATES_DIR / template_name
    if not html_path.exists():
        return None
    with open(html_path, "r", encoding="utf-8") as file_handle:
        return file_handle.read()


def _start_monitor_engine(ticker: str, timeframe: str) -> Tuple[bool, str]:
    """Start the monitor in a background thread to avoid blocking the API."""
    global monitor_engine, monitor_thread

    with monitor_lock:
        if monitor_engine and monitor_engine.running:
            return False, "already running"
        if monitor_thread and monitor_thread.is_alive():
            return False, "initializing"

        def run_engine() -> None:
            global monitor_engine
            try:
                engine = RealTimeMonitor(
                    ticker=ticker,
                    timeframe_str=timeframe,
                    ui_callback=None,
                )
                engine.event_bus.subscribe("INFERENCE_SIGNAL", handle_inference_signal)
                engine.event_bus.subscribe("INFERENCE_SIGNAL", cache_signal)
                monitor_engine = engine
                engine.start_time = datetime.now()
                engine.start()
            except Exception as exc:
                logger.error(f"Error starting monitor engine: {exc}")
                monitor_engine = None

        monitor_thread = threading.Thread(target=run_engine, daemon=True)
        monitor_thread.start()
        return True, "starting"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    logger.info("Starting FastAPI application...")

    _start_monitor_engine(settings.TICKER_TARGET, "M5")

    yield

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

# Register routers
app.include_router(chart_data_router)


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
    """Root endpoint - serves home template."""
    html_content = _read_template("home.html")
    if html_content:
        return HTMLResponse(content=html_content)

    return {
        "service": "WTNPS Trade Live Monitor API",
        "version": "3.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "message": "HTML template not found. API endpoints are available.",
    }


@app.get("/charts", tags=["UI"])
async def charts():
    """Charts endpoint - serves charting template."""
    html_content = _read_template("charts_clean.html")
    if html_content:
        return HTMLResponse(content=html_content)

    return JSONResponse(
        status_code=404,
        content={
            "error": "Charts template not found",
            "timestamp": datetime.now().isoformat(),
        },
    )


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
    started, reason = _start_monitor_engine(ticker, timeframe)

    if not started:
        return JSONResponse(
            status_code=400,
            content={"error": f"Monitor {reason}"},
        )

    return {
        "status": "starting",
        "ticker": ticker,
        "timeframe": timeframe,
        "timestamp": datetime.now().isoformat(),
    }


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
    """Deprecated: kept for backward compatibility."""
    logger.warning("run_monitor_loop is deprecated; use _start_monitor_engine instead.")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
