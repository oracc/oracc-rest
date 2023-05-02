# this file is used for deploying the flask application on a production server
# follow the README instructions for the full deployment process

import sys
sys.path.insert(0, '/var/www/oracc-rest')

from app import app as application
