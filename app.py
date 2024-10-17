import logging
import os
from datetime import datetime
from flask import Flask, current_app, jsonify
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

# Bonsai credentials and URL
BONSAI_HOST = os.getenv('BONSAI_HOST')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')

# Set up Elasticsearch client
es = Elasticsearch(
    [{'host': BONSAI_HOST, 'port': 443, 'use_ssl': True}],
    http_auth=(ACCESS_KEY, ACCESS_SECRET)
)

# Create Flask application
app = Flask(__name__)

# Create index for logs if it doesn't exist
index_name = 'logs'
try:
    es.indices.create(index=index_name)
except NotFoundError:
    pass  # Index already exists
except Exception as e:
    print("Error creating index:", e)

# Custom logging handler for Elasticsearch
class ElasticSearchHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        # Prepare the log entry for Elasticsearch
        doc = {
            'timestamp': datetime.now(),
            'level': record.levelname,
            'message': log_entry,
            'service': 'my_flask_app'
        }
        # Index the log entry in Elasticsearch
        es.index(index=index_name, body=doc)

# Set up the Elasticsearch logging handler
handler = ElasticSearchHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s :: %(levelname)-8s :: %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

@app.route('/')
def hello_world():
    current_app.logger.info("hello world logger")
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0")
