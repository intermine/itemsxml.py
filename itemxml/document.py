from itemxml.item import Item

class Factory:

    def __init__(self, model):
        self.items = {}
        self.id_counter = 0
        self.model = model

    def get_next_id(self):
        obj_id = self.id_counter
        self.id_counter = self.id_counter + 1
        return obj_id

    def create_item(self, classnames, properties = None):
        i = self.get_next_id()
        item = Item(self.model, i, classnames, properties)
        item.validate()
        return item

    def add(self, classnames, properties = None):
        item = self.create_item(classnames, properties)
        self.items[item.get('id')] = item
        return item

    def __iter__(self):
        for idx in range(self.id_counter):
            yield self.items[idx]

