# this file is used for deploying the flask application on a production server
# follow the readme instructions for the deployment process

import sys
sys.path.insert(0, '/var/www/flask/oracc-rest')

from app import app

application = app
