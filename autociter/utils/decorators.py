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
"""Define useful and frequently needed decorators."""
from threading import Thread
import functools


class TimeoutException(Exception):
    """Exception raised by timeout decorator."""
    pass


# Adapted from code by Stackoverflow users acushner and Almenon.
# https://stackoverflow.com/questions/21827874/timeout-a-python-function-in-windows
def timeout(seconds_before_timeout):
    """Raise TimeoutException after some amount of time."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [
                Exception('function [%s] timeout [%s seconds] exceeded!' %
                          (func.__name__, seconds_before_timeout))
            ]

            def helper():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as error:  #pylint: disable=broad-except
                    res[0] = error

            thread = Thread(target=helper)
            thread.daemon = True
            thread.start()
            thread.join(seconds_before_timeout)
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret

        return wrapper

    return decorator
