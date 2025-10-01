"""Constants for Kleinanzeigen MCP."""

# API Limits
API_MAX_LIMIT = 10  # Maximum items per API request
DEFAULT_LIMIT = 10  # Default number of items to fetch
MAX_IMAGE_DISPLAY = 5  # Maximum number of images to display in details

# Text Display Limits
DESCRIPTION_PREVIEW_LENGTH = 200  # Characters to show in description preview
MAX_QUERY_LENGTH = 500  # Maximum length for search query
MAX_LOCATION_LENGTH = 100  # Maximum length for location string

# Request Limits
DEFAULT_REQUEST_TIMEOUT = 30.0  # Default timeout in seconds
MAX_RETRIES = 3  # Maximum number of retries for failed requests
RETRY_DELAY = 1.0  # Initial delay between retries in seconds

# Rate Limiting
RATE_LIMIT_REQUESTS = 60  # Maximum requests per window
RATE_LIMIT_WINDOW = 60  # Rate limit window in seconds

# Validation
MIN_PRICE = 0
MAX_PRICE = 999999999
MIN_RADIUS = 1
MAX_RADIUS = 200
MIN_PAGE_COUNT = 1
MAX_PAGE_COUNT = 20

# Sort Options
VALID_SORT_OPTIONS = ["newest", "oldest", "price_asc", "price_desc"]
DEFAULT_SORT = "newest"