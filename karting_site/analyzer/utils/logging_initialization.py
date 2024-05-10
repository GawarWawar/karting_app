import logging    
import os.path
        
# Create logger to make logs
def get_or_create_logger_for_race (
    log_level: str = "INFO",
    race_id: int|None = None,
    logger_name:str|None = None
):
    """
    Get or create a logger for a specific race.

    Parameters:
        log_level (str, optional): The logging level. Defaults to "INFO".
        race_id (int, optional): The ID of the race. Defaults to None.
        logger_name (str, optional): The name of the logger.
            Defaults to None (uses a default naming convention).

    Returns:
        logging.Logger: The logger object.

    Raises:
        TypeError: If both race_id and logger_name are None.
    """
    if race_id is None and logger_name is None:
        raise TypeError ("Either race_id or file_name_for_logger should have a vallue, which is not None")
    
    logger_name = logger_name or f"race_id_{race_id}"
        
    race_logger = logging.getLogger(logger_name)
    race_logger.setLevel(log_level)
    
    return race_logger
                
def create_and_assign_filehandler_to_logger (
    race_logger: logging.Logger,
    race_id:int|None = None,
    file_name_for_logger: str|None = None,
):
    """
    Create and assign a file handler to a logger.

    Parameters:
        race_logger (logging.Logger): The logger object.
        race_id (int, optional): The ID of the race. Defaults to None.
        file_name_for_logger (str, optional): The name of the logger and file.
            Defaults to None (uses a default naming convention).

    Returns:
        logging.FileHandler: The file handler object.
    """
    if race_id is None and file_name_for_logger is None:
        raise TypeError ("Either race_id or file_name_for_logger should have a vallue, which is not None")
    
    file_name_for_logger = file_name_for_logger or f"race_id_{race_id}"
         
    # FileHandler change for logger, to change logger location
    file_handler = logging.FileHandler(
        os.path.join(
            'analyzer', 'data', 'logs', 'analyzer.log'
        )
    )
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    race_logger.addHandler(file_handler)
    
    return file_handler