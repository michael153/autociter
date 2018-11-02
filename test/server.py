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
import http.server
import socketserver
import threading
import os

HOST, PORT = "localhost", 8000

server = None
url = "http://" + HOST + ":" + str(PORT)
# Relocate to directory with index.html
os.chdir(os.path.dirname(__file__))


class CustomHandler(http.server.SimpleHTTPRequestHandler):

	# Disable output from handler
	def log_message(self, format, *args):
		return ""


class CustomServer(socketserver.TCPServer):

	# Allow address reuse to prevent errors
	allow_reuse_address = True


def start():
	global server
	if not server:
		server = CustomServer((HOST, PORT), CustomHandler)
		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.start()


def end():
	global server
	if server:
		server.shutdown()
		server.server_close()
		server = None
