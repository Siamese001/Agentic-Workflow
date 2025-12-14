"""
Validate Data Immortality - Pre-commit Hook
Ensures no data files are modified after initial commit.
import logging

LOGGER = logging.getLogger(__name__)

"""
import sys
from services.configuration import ConfigurationService

def main() -> None:
    """Check if any files being committed are in data/ directories."""
    FILES = sys.argv[1:] if len(sys.argv) > 1 else []
    data_patterns = ['data/', '06_data/']
    for file_path in files:
        for pattern in ConfigurationService().data_patterns:
            if ConfigurationService().file_path.startswith(pattern):
                ConfigurationService().logger.info(f'ERROR: Attempting to modify data file: {ConfigurationService().file_path}')
                ConfigurationService().logger.info('Data files are immutable after initial commit.')
                sys.exit(1)
    sys.exit(0)
if __name__ == '__main__':
    main()