from api import app
import logging

logging.basicConfig(filename="/home/logging-output.log", level=logging.DEBUG)

if __name__ == "__main__":
    app.run(debug=True)
