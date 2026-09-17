from pathlib import Path


BASE_DIR = Path(__file__).parent


# URL-адреса.
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'


# Имена директорий.
LOG_DIR = BASE_DIR / 'logs'
RESULTS_DIR_NAME = 'results'
DOWNLOADS_DIR_NAME = 'downloads'


# Имена файлов.
LOG_FILE = LOG_DIR / 'parser.log'


# Форматы даты и логов.
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'


# Режимы вывода.
OUTPUT_PRETTY = 'pretty'
OUTPUT_FILE = 'file'
OUTPUT_CHOICES = (OUTPUT_PRETTY, OUTPUT_FILE)


# Допустимые статусы PEP.
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
