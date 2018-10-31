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


def csv(item):
    """Return the csv-valid representation of an object."""
    return type(item).__csv__(item)


class Table:
    """A generic data table."""

    DELIMITER = "\t"

    def __init__(self, filename=None, fields=(), records=()):
        """Initialize a data table.

        Arguments:
            fields: A list of attribute names.
            records: A list of Record objects.
            filename: The name of a data sheet.
        """
        self.records = []
        if filename:
            self.load(filename)
        else:
            if not fields:
                raise ValueError("Expected at least one field.")
            self.fields = fields
            for record in records:
                self.add(record)

    def load(self, filename):
        """Load data from a file."""
        with open(filename, encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.fields = lines[0].split(self.DELIMITER)
        for line in lines[1:]:
            self.add(parse(line))

    def parse(line):
        """Parse a line of text that represents a data record."""
        values = line.split(self.DELIMITER)
        return Record(self.fields, values)

    def save(self, filename):
        """Save data to a file."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(self.header + "\n")
            for record in self.records:
                file.write(csv(record) + "\n")

    @property
    def header(self):
        """A string representing this table's header."""
        header = ""
        for field in self.fields:
            header += field + self.DELIMITER
        return header.rstrip()

    def query(self, function):
        """Return a Table containing records that satisfy some function."""
        valid = [r for r in self.records if function(r)]
        return Table(fields=self.fields, records=valid)

    def add(self, record):
        if not isinstance(record, Record):
            raise TypeError("Expected Record object.")
        if record.fields != self.fields:
            raise ValueError("Table and record fields are mismatched.")
        self.records.append(record)

    def __getitem__(self, key):
        return self.records[key]

    def __len__(self):
        return len(self.records)


class Record:
    """A record in a data table."""

    LABEL_SIZE = 5
    DELIMITER = "\t"

    def __init__(self, fields, values):
        self.fields = fields
        self.values = values
        self.data = dict(zip(fields, values))

    def __getitem__(self, field):
        return self.data.get(field, "")

    def __contains__(self, field):
        return bool(self.data.get(field, ""))

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return self.data == other.data

    def __csv__(self):
        """Return csv-compatible representation."""
        string = ""
        for field in self.data:
            string += self.data[field] + self.DELIMITER
        return string.rstrip()

    def __repr__(self):
        fields = list(self.data.keys())
        values = list(self.data.values())
        return "Record({0}, {1})".format(fields, values)

    def __str__(self):
        string = ""
        for field in self.data:
            if self.data[field]:
                string += field[:self.LABEL_SIZE] + self.DELIMITER
                string += str(self.data[field]) + "\n"
        return string.rstrip()
