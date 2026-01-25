class IngestionError(Exception):
    """
    Base class for all ingestion-related errors.
    """
    pass


class ConfigError(IngestionError):
    """
    Raised when configuration is missing or invalid.
    """
    pass


class ExternalAPIError(IngestionError):
    """
    Raised when an external API call fails.
    """
    pass


class FileOperationError(IngestionError):
    """
    Raised when file-level operations fail.
    """
    pass
