import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Set up logging configuration for the application.
    """
    # Create logger
    logger = logging.getLogger("todo_ai_chatbot")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers if already configured
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Initialize the logger
logger = setup_logging(
    log_level="INFO",
    log_file=f"logs/todo_ai_chatbot_{datetime.now().strftime('%Y%m%d')}.log"
)


def log_info(message: str):
    """Log an info message."""
    logger.info(message)


def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)


def log_error(message: str):
    """Log an error message."""
    logger.error(message)


def log_debug(message: str):
    """Log a debug message."""
    logger.debug(message)