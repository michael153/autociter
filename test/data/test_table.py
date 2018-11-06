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
"""Test methods of the Table object defined in data.storage."""
import unittest
import filecmp
import os

from autociter.data.storage import Table, Record
import assets


# pylint: disable=missing-docstring,
class TableTest(unittest.TestCase):

    def setUp(self):
        self.filename = assets.MOCK_DATA_PATH + "/mock_table_data.csv"

    def test_init(self):
        table = Table(fields=["shoe", "color"])
        self.assertEqual(len(table), 0)

    def test_load(self):  #pylint: disable=invalid-name
        table = Table(fields=["id", "first", "last", "department"])
        records = [
            Record(table.fields, ["0316", "Balaji", "Veeramani", "Statistics"]),
            Record(table.fields, ["4164", "Grace", "Chen", "Mathematics"]),
            Record(table.fields, ["1738", "Michael", "Wan", "EECS"]),
            Record(table.fields, ["6123", "Derek", "Waleffe", "Mathematics"])
        ]
        for record in records:
            table.add(record)
        self.assertEqual(Table(self.filename), table)

    def test_parse(self):
        table = Table(fields=["name", "number"])
        record = table.parse("Balaji\t521-834-7037")
        self.assertEqual(record.fields, ["name", "number"])
        self.assertEqual(record.values, ["Balaji", "521-834-7037"])

    def test_save(self):
        table = Table(self.filename)
        table.save("temp_test_data.csv")
        files_are_identical = filecmp.cmp(self.filename, "temp_test_data.csv")
        self.assertTrue(files_are_identical)
        os.remove("temp_test_data.csv")

    def test_find(self):
        table = Table(self.filename)
        record = Record(table.fields, ["1738", "Michael", "Wan", "EECS"])
        self.assertEqual(table.find("department", "EECS"), record)
        self.assertEqual(table.find("department", "Chemistry"), None)

    def test_header(self):
        table = Table(fields=["name", "number"])
        self.assertEqual(table.header, "name\tnumber")

    def test_query(self):
        table = Table(self.filename)

        def in_math_department(record):
            return record["department"] == "Mathematics"

        queried = table.query(in_math_department)
        self.assertEqual(len(queried), 2)

    def test_query_is_nondestructive(self):
        table = Table(self.filename)
        backup = Table(self.filename)
        table.query(lambda record: False)
        self.assertEqual(table, backup)

    def test_get_item(self):
        table = Table(fields=["player", "power level"])
        record = Record(table.fields, ["Rafael Nadal", 9001])
        table.add(record)
        self.assertEqual(table[0], record)

    def test_add_with_custom_key(self):
        table = Table(fields=["flavor", "rating"])
        record = Record(table.fields, ["vanilla", 7.8])
        table.add(record, "vanilla")
        self.assertEqual(table["vanilla"], record)

    def test_add_with_wrong_type(self):
        table = Table(fields=["flavor", "rating"])
        with self.assertRaises(TypeError):
            table.add(3)

    def test_add_with_invalid_fields(self):
        table = Table(fields=["flavor", "rating"])
        record = Record(["name", "number"], ["Bryson", "812-351-1423"])
        with self.assertRaises(ValueError):
            table.add(record)

    def test_add_with_duplicate_key(self):
        table = Table(fields=["flavor", "rating"])
        record1 = Record(table.fields, ["vanilla", 7.8])
        table.add(record1)
        record2 = Record(table.fields, ["chocolate", 5.3])
        with self.assertRaises(ValueError):
            table.add(record2, 0)

    def test_get_item_with_invalid_key(self):
        table = Table(fields=["name", "number"])
        with self.assertRaises(KeyError):
            table[27345]  # pylint: disable=pointless-statement

    def test_get_item_with_custom_key(self):
        table = Table(fields=["player", "power level"])
        record = Record(table.fields, ["Rafael Nadal", 9001])
        table.add(record, "Mallorca")
        self.assertEqual(table["Mallorca"], record)

    def test_contains(self):
        table = Table(fields=["name", "GPA"])
        record1 = Record(table.fields, ["Bryson Bauer", 3.34])
        record2 = Record(table.fields, ["Ian Fumusa", 2.27])
        for record in [record1, record2]:
            table.add(record)
        self.assertTrue(record1 in table)

    def test_len(self):
        table = Table(self.filename)
        self.assertEqual(len(table), 4)

    def test_extend(self):
        table = Table(fields=["name", "GPA"])
        records = [
            Record(table.fields, ["Bryson Bauer", 3.34]),
            Record(table.fields, ["Ian Fumusa", 2.27])
        ]
        table.extend(records)
        self.assertTrue(len(table) == 2)
        self.assertEqual(table[0], records[0])
        self.assertEqual(table[1], records[1])

    def test_iter(self):
        table = Table(fields=["name", "GPA"])
        record1 = Record(table.fields, ["Bryson Bauer", 3.34])
        record2 = Record(table.fields, ["Ian Fumusa", 2.27])
        for record in [record1, record2]:
            table.add(record)
        self.assertEqual([record for record in table], [record1, record2])

    def test_equals(self):
        table1 = Table(self.filename)
        table2 = Table(self.filename)
        self.assertEqual(table1, table2)
