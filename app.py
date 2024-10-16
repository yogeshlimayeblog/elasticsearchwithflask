import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, current_app
from elasticsearch import Elasticsearch

# Flag for whether to log remotely to Elasticsearch or locally to a file
is_remote = True

# Define the app root and log file path
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILENAME = f"{APP_ROOT}/logs/api.log"

# Flask app instance
app = Flask(__name__)

# Elasticsearch configuration for logging setup
if is_remote:
    # Set up the Elasticsearch client (assuming Elasticsearch runs in Docker with the name `elasticsearch`)
    es = Elasticsearch(
        ["https://172.19.0.2:9200"],  # Use HTTPS and the container name for Docker
        verify_certs=False,              # Disable SSL verification for testing (not recommended for production)
        basic_auth=("elastic", "5VhupIKx54o6t+SSQJuF")  # Replace with your actual elastic user password
    )

    class ElasticsearchHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            # Send the log entry to Elasticsearch as a document
            es.index(index="flask", document={"message": log_entry, "App": "elasticsearchwithflask", "Environment": "Dev"})

    # Use custom handler for Elasticsearch logging
    handler = ElasticsearchHandler()
else:
    # Local file logging setup if `is_remote` is False
    if not os.path.exists(os.path.dirname(LOG_FILENAME)):
        os.makedirs(os.path.dirname(LOG_FILENAME))
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=10)

# Set up logging handler and format
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s :: %(levelname)-8s :: %(message)s")
handler.setFormatter(formatter)

# Add handler to Flask app logger
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# Set up a separate logger for testing
log = logging.getLogger("PythonTest")
log.setLevel(logging.INFO)
log.addHandler(handler)

# Test log
log.info("Test logs initialized")

# Flask route
@app.route('/')
def hello_world():
    current_app.logger.info("Hello World logger")
    return 'Hello World!'

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0")
