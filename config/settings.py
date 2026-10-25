# Application Settings

# Password Configuration
ACTIVATION_PASSWORD = "Zhang"
MAX_PASSWORD_ATTEMPTS = 3

# Display Settings
PROGRESS_BAR_WIDTH = 75
LOADING_ANIMATION_DURATION = 0.1
LOADING_ANIMATION_ITERATIONS = 20

# Search Settings
VALID_PHONE_PREFIX = "08"
NIK_LENGTH = 16

# Export Settings
EXPORT_DIR = "exports"
EXPORT_FORMATS = ["json", "csv", "txt"]

# History Settings
MAX_HISTORY_ITEMS = 50

# Batch Search Settings
BATCH_INPUT_FILE = "batch_search.txt"
MAX_BATCH_SIZE = 100

# New Features Settings
QUICK_SEARCH_MODE = False
MAX_FAVORITES = 20
PHONE_OPERATORS = {
    "0811": "Telkomsel", "0812": "Telkomsel", "0813": "Telkomsel", 
    "0821": "Telkomsel", "0822": "Telkomsel", "0823": "Telkomsel",
    "0852": "Telkomsel", "0853": "Telkomsel",
    "0814": "Indosat", "0815": "Indosat", "0816": "Indosat",
    "0855": "Indosat", "0856": "Indosat", "0857": "Indosat", "0858": "Indosat",
    "0817": "XL", "0818": "XL", "0819": "XL", "0859": "XL", "0877": "XL", "0878": "XL",
    "0831": "Axis", "0832": "Axis", "0833": "Axis", "0838": "Axis",
    "0895": "Three", "0896": "Three", "0897": "Three", "0898": "Three", "0899": "Three",
    "0881": "Smartfren", "0882": "Smartfren", "0883": "Smartfren", "0884": "Smartfren",
    "0885": "Smartfren", "0886": "Smartfren", "0887": "Smartfren", "0888": "Smartfren", "0889": "Smartfren"
}
SOCIAL_MEDIA_PLATFORMS = ["Instagram", "Facebook", "Twitter", "TikTok"]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

# Colors
COLORS = {
    "INFO": "cyan",
    "WARNING": "yellow",
    "ERROR": "red",
    "SUCCESS": "green"
}
