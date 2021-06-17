import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, current_app
from cmreslogging.handlers import CMRESHandler

is_remote = True
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print (APP_ROOT)
LOG_FILENAME = f"{APP_ROOT}/logs/api.log"
app = Flask(__name__)
if (is_remote):
    handler = CMRESHandler(hosts=[{'host': 'localhost', 'port': 9200}],
                           auth_type=CMRESHandler.AuthType.NO_AUTH,
                           es_index_name="flask",
                           es_additional_fields={'App': 'elasticsearchwithflask', 'Environment': 'Dev'})
else:
    if not os.path.exists(os.path.dirname(LOG_FILENAME)):
        os.makedirs(os.path.dirname(LOG_FILENAME))
    handler = RotatingFileHandler(LOG_FILENAME, maxBytes = 10000000, backupCount = 10)

handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("logging.Formatter(fmt=' %(name)s :: %(levelname)-8s :: %(message)s')")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
log = logging.getLogger("PythonTest")
log.setLevel(logging.INFO)
log.addHandler(handler)
log.info("test logs")

@app.route('/')
def hello_world():
    current_app.logger.info("hello world logger")
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host="0.0.0.0")