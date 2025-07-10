import os
import logging
from datetime import datetime

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger("payroll_auditor")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/payroll_auditor_{timestamp}.log", encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logger() 