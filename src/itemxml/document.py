from itemxml.item import Item

def get_model():
    from os.path import join, dirname
    import intermine.model
    return intermine.model.Model(join(dirname(__file__), '..', '..', 'resources', 'testmodel_model.xml'))

class Factory:

    def __init__(self, model):
        self.items = {}
        self.id_counter = 0
        self.model = model

    # The public API:

    def add(self, *classnames, **properties):
        """Add an Item to this Document

        >>> document = Factory(get_model())
        >>> emp = document.add('Employee', name = 'Anne')
        >>> print len(document)
        1
        >>> print emp.get('name')
        Anne
        """
        item = self.create(*classnames, **properties)
        self.items[item.get('id')] = item
        return item

    def create(self, *classnames, **properties):
        """Create an Item, but remember nothing about it.

        >>> document = Factory(get_model())
        >>> emp = document.create('Employee', name = 'Anne')
        >>> print len(document)
        0
        >>> print emp.get('name')
        Anne
        """
        i = self._get_next_id()
        item = Item(self.model, i, classnames, properties)
        item.validate()
        return item

    def __len__(self):
        return len(self.items)

    def get(self, itemid):
        return self.items[itemid]

    def search(self, classname, properties):
        for item in filter(lambda i: self._wanted(classname, properties, i), self.items.values()):
            yield item

    def __iter__(self):
        for idx in xrange(self.id_counter):
            yield self.items[idx]

    # Private API

    def _get_next_id(self):
        obj_id = self.id_counter
        self.id_counter = self.id_counter + 1
        return obj_id

    def _wanted(self, classname, properties, item):
        class_ok = classname in item.classnames or any(cd.isa(classname) for cd in item.classes)

        item_props = item.properties.items()
        return class_ok and all(pair in item_props for pair in properties.iteritems())

