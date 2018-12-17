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
"""Implements command-line interface and high-level functionality."""
import argparse
import sys

from autociter.core.errors import AutociterError

__version__ = '0.0.0'


def main(argv):
    """Main program.

  Arguments:
      argv: command-line arguments, such as sys.argv (including the program name
            in argv[0]).

  Returns:
      Zero on successful program termination, non-zero otherwise.
  """
    parser = argparse.ArgumentParser(description='Automated citation tool.')
    parser.add_argument(
        '-v',
        '--version',
        action='store_true',
        help='show version number and exit')
    parser.add_argument(
        '--style', action='store', help='specify formatting style')
    parser.add_argument(
        '-vv',
        '--verbose',
        action='store_true',
        help='display all extracted data')
    parser.add_argument('urls', nargs='*', help='specify which URLs to cite.')
    args = parser.parse_args(argv[1:])

    if args.version:
        print('autociter {}'.format(__version__))
        return 0

    return 0


def run_main():
    """Run main method and return appropriate exit code."""
    try:
        sys.exit(main(sys.argv))
    except AutociterError as e:  #pylint: disable=invalid-name
        sys.stderr.write('autociter: ' + str(e) + '\n')
        sys.exit(1)


if __name__ == '__main__':
    run_main()
