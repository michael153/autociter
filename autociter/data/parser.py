from wikibot import Reference
REQUIRED_FIELDS = "url"
DELIMITER = "\t"

def create(filename, overwrite=False):
    with open(filename, "w", encoding="utf-8") as file:
        header = ""
             header += attribute + "\t"
        file.write(header.rstrip() + "\n")


def write(records, filename):
    valid_records = filter(validate, records)
    with open(filename, "a", encoding="utf-8") as file:
        for record in valid_records:
            file.write(str(record) + "\n")


def validate(record):
    if type(record) is not Record:
        return False
    for attribute in REQUIRED_FIELDS:
        if not attribute in reference:
            return False
    return True


class Table:
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
