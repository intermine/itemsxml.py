class XMLWriter:

    def __init__(self, f):
        self._f = f

    def begin(self):
        pass

    def write_item(self, item):
        pass

    def end(self):
        pass

def write_itemsxml(filename, items):
    written = set()

    with open(self.filename) as f:
        xml_writer = XMLWriter(f)

        xml_writer.begin()

        for item in items:
            item_id = item.get('id')
            if item_id not in written:
                xml_writer.write_item(item)
                written.add(item_id)

        xml_writer.end()

