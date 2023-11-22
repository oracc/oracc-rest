from api import app
import logging

# logging.basicConfig(filename="/home/rits/logging-output.log", level=logging.DEBUG)
logging.basicConfig(
    filename="/home/rits/logging-output.log",
    level=logging.DEBUG,
    format="%(levelname)8s | [%(asctime)s] | %(name)s | %(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


if __name__ == "__main__":
    app.run(debug=True)
