import logging
import sys

# Configure a basic logger
logger = logging.getLogger("collectors")
logger.setLevel(logging.INFO)

# Create console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
if not logger.hasHandlers():
    logger.addHandler(ch)
