import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging(environment: str = "development") -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if environment != "development" else logging.DEBUG)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    
    if environment == "production":
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Set levels for third-party packages to avoid noise
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
