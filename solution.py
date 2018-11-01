from urllib import error, request
from socket import timeout

from data.storage import Table
from data.queries import contains

from datetime import datetime
i = 0
print("Starting at {0}.".format(datetime.now()))

def openable(record):
    global i
    i += 1
    print(i/109229, end="\r")
    """Return true if the record url attribute is openable."""
    try:
        request.urlopen(record["url"], timeout=10)
        return True
    except (error.HTTPError, error.URLError, timeout, ValueError) as e:
        return False
    except:
        log(record["url"])


def log(message, filename="log.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(message + "\n")


table = Table("resources/data.txt")
table.query(openable).save("clean.txt")
print("Ending at {0}.".format(datetime.now()))
