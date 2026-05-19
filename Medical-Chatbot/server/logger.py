import logging

def setup_logger(name="MedicalAssistent"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    formater = logging.Formatter("[%(asctime)s] [%(levelname)s] --- [%(message)s]")
    ch.setFormatter(formater)
    
    if not logger.hasHandlers():
        logger.addHandler(ch)
        
    return logger


logger=setup_logger()

logger.info("RAG process started")
logger.debug("Debugging")
logger.error("Failed to load")
logger.critical("Critical Message")