# Copyright 2018 Balaji Veeramani, Michael Wan
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# Author: Balaji Veeramani <bveeramani@berkeley.edu>
"""Define functions for running a mock website."""
import http.server
import socketserver
import threading
import os

import assets

HOST, PORT = "localhost", 8000
ADDRESS = "http://" + HOST + ":" + str(PORT)

# Relocate to the directory with mock html files
os.chdir(assets.WEBPAGES_PATH)
server = None  # pylint: disable=invalid-name


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler does NOT print to the console."""

    # Disable output from handler
    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        return ""


class CustomServer(socketserver.TCPServer):
    """Custom TCP server that is less prone to errors."""

    # Allow address reuse to prevent errors
    allow_reuse_address = True


def start():
    """Start the mock website."""
    global server  # pylint: disable=invalid-name, global-statement,
    if not server:
        server = CustomServer((HOST, PORT), CustomHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()


def end():
    """Shutdown the mock website and clean up."""
    global server  # pylint: disable=invalid-name, global-statement
    if server:
        server.shutdown()
        server.server_close()
        server = None
