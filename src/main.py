"""Demo entrypoint that serves the API and UI."""

import os

import uvicorn


def run() -> None:
    host = os.getenv("WTNPS_HOST", "0.0.0.0")
    port = int(os.getenv("WTNPS_PORT", "8000"))
    reload_enabled = os.getenv("WTNPS_RELOAD", "false").lower() == "true"
    log_level = os.getenv("WTNPS_LOG_LEVEL", "info")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=reload_enabled,
        log_level=log_level,
    )


if __name__ == "__main__":
    run()
