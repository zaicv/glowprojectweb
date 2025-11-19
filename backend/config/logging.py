"""
📋 Logger Setup - Stage Manager's Clipboard
Configures human-friendly logging for GlowGPT
"""
import logging

# ----------------------------
# Human-friendly logging formatter
# ----------------------------
class SimpleFormatter(logging.Formatter):
    """
    Format logs nicely for humans:
    - Show timestamp + message
    - Only show level for warnings/errors
    """
    def format(self, record):
        # Generate timestamp manually
        record_time = self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S")
        
        # Show level only for warnings/errors
        prefix = ""
        if record.levelno >= logging.WARNING:
            prefix = f"[{record.levelname}] "
        
        return f"{record_time} {prefix}{record.getMessage()}"

# ----------------------------
# Configure logger
# ----------------------------
logger = logging.getLogger("GlowGPT")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(SimpleFormatter())
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler("glowgpt.log", mode="a")
file_handler.setFormatter(SimpleFormatter())
logger.addHandler(file_handler)

# ----------------------------
# Silence noisy loggers (uvicorn/httpx)
# ----------------------------
for log_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "httpx"]:
    l = logging.getLogger(log_name)
    l.setLevel(logging.WARNING)  # Only warnings/errors
    l.handlers = [logging.StreamHandler()]

# Export logger for use throughout the app
__all__ = ["logger"]