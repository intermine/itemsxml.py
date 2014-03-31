import loxun
import sys
from contextlib import closing

class EmptyValueError(Exception):

    def __init__(self, name):
        Exception.__init__(self, "no value supplied for " + name)

class XMLWriter(object):

    DEFAULT_PREFIX = "0_"

    def __init__(self, f, prefix = None, allow_none = True):
        if prefix is None:
            self.prefix = XMLWriter.DEFAULT_PREFIX
        else:
            self.prefix = prefix

        self.raise_error_on_empty_value = not allow_none

        self.writer = loxun.XmlWriter(f)
        self.written = set()

    def begin(self):
        self.writer.startTag("items")

    def write_item(self, item):
        item_id = item.get('id')
        if item_id not in self.written:
            self._write_item(item)
            self.written.add(item_id)

    def _write_item(self, item):
        cname = item.classname
        impls = item.implements
        item_attr = {
            "id": self.prefix + str(item.get("id")),
            "class": cname if cname is not None else '',
            "implements": " ".join(impls)
        }
        self.writer.startTag("item", item_attr)
        for key in item.properties.keys():
            if key != "id":
                self.write_item_property(item, key)
        self.writer.endTag()

    def write_item_property(self, item, name):
        value = item.get(name)
        if value is None and self.raise_error_on_empty_value:
            raise EmptyValueError(name)
        else:
            fd = item.get_field_descriptor(name)
            if fd.fieldtype == "collection":
                self.write_collection(value, name)
            elif fd.fieldtype == "reference":
                self.write_reference(value, name)
            else:
                self.writer.tag("attribute", {"name": name, "value": value})

    def write_collection(self, coll, name):
        self.writer.startTag("collection", {"name": name})
        map(self.write_reference, coll)
        self.writer.endTag()

    def write_reference(self, ref, name = None):
        attrs = {"ref_id": self.prefix + str(ref.get("id"))}
        if name is not None:
            attrs['name'] = name
        self.writer.tag("reference", attrs)

    def end(self):
        self.writer.endTags()
        self.writer.close()

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        self.end()

    def write_items(self, items):
        for item in items:
            self.write_item(item)

def write_itemsxml(items, filename = None):

    def writeitems(out):
        with XMLWriter(out) as writer:
            writer.write_items(items)

    if filename is None:
        writeitems(sys.stdout)
    else:
        with closing(open(filename, 'w')) as f:
            writeitems(f)

