import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures structured console logging for the command center backend."""
    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] "
        "[SIMULATION_MODE=" + str(settings.IS_SIMULATION_MODE) + "] - %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logger = logging.getLogger("disaster_command")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    return logger


logger = setup_logging()
