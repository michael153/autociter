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
"""Test decorators defined in autociter.utils.decorators."""
import time
import unittest

from autociter.utils.decorators import timeout, TimeoutException


# pylint: disable=missing-docstring
class DecoratorTest(unittest.TestCase):

    def test_timeout(self):

        @timeout(5)
        def wait(seconds):
            time.sleep(seconds)

        try:
            wait(1)
        except TimeoutException:
            self.fail("Unexpected TimeoutException")
        with self.assertRaises(TimeoutException):
            wait(10)
