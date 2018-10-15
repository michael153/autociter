DELIMITER = "\t"

class Table:
    """Example:
    >>> t = Table("assets/data.txt")
    >>> t[0]["url"]
    "http://www.iwm.org.uk/memorials/item/memorial/2814"
    >>> urls = [r["url"] for r in t.records]
    """
    def __init__(self, filename):
        with open(filename, encoding="utf-8") as file:
            lines = file.read().splitlines()
        self.fields, records_raw = lines[0].split(DELIMITER), lines[1:]
        self.records = [Record(self.fields, string.split(DELIMITER)) for string in records_raw]

    def __getitem__(self, key):
        return self.records[key]

    def __len__(self):
        return len(self.records)

class Record:

    def __init__(self, fields, values):
        self.mapping = dict(zip(fields, values))

    def __getitem__(self, field_name):
        return self.mapping.get(field_name, "null")
