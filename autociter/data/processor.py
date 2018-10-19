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
"""Define function and objects for manipulating data files."""
DELIMITER = "\t"


def create(filename, attributes=()):
    """Create new data file with a header."""
    with open(filename, "w", encoding="utf-8") as file:
        header = ""
        for attribute in attributes:
            header += attribute + DELIMITER
        newline = "\n" if attributes else ""
        file.write(header.rstrip() + newline)


def write(records, filename):
    """Write data records to a file."""
    with open(filename, "a", encoding="utf-8") as file:
        for record in records:
            file.write(csv(record) + "\n")


def csv(object):
    """Return the csv-valid representation of an object."""
    return type(object).__csv__(object)

class Table:
    """A generic data table."""

    def __init__(self, fields=(), records=(), filename=None):
        """Initializes data table.

        If a filename is given, the file at that path is loaded and its data
        is imported. Otherwise, an empty table is created.

        Arguments:
            fields: A list of attribute names.
            records: A list of Record objects.
            filename: The name of a data sheet.
        """
        self.fields = fields
        self.records = records
        if filename:
            self.load(filename)

    def load(self, filename):
        """Destructively loads data from a file."""
        with open(filename, encoding="utf-8") as file:
            lines = file.read().splitlines()
        header, raws = lines[0], lines[1:]
        self.fields = header.split(DELIMITER)
        self.records = [Record(self.fields, r.split(DELIMITER)) for r in raws]

    def query(self, function):
        """Return a Table containing records that satisfy some function."""
        valid = [r for r in self.records if function(r)]
        return Table(self.fields, valid)

    def __getitem__(self, key):
        return self.records[key]

    def __len__(self):
        return len(self.records)


class Record:
    """A record in a data table."""

    def __init__(self, fields, values):
        self.data = dict(zip(fields, values))

    def __getitem__(self, field):
        return self.data.get(field, "")

    def __contains__(self, field):
        return bool(self.data.get(field, False))

    def __csv__(self):
        """Return csv-compatible representation."""
        string = ""
        for field in self.data:
            string += self.data[field] + DELIMITER
        return string.rstrip()

    def __str__(self):
        string = ""
        for attribute in self.data:
            if self.data[attribute]:
                string += attribute[0:5] + "\t" + self.data[attribute] + "\n"
        return string
