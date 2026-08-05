import logging

def setup_logging():
    """Set up logging configuration for the GameCache project."""

    # Show INFO-level progress (e.g. BGG collection generation retries) by
    # default, without requiring --debug.
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Set the logging level for specific libraries to WARNING to suppress DEBUG messages
    logging.getLogger("PIL").setLevel(logging.WARNING)
