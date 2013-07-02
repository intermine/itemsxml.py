import itemxml.item.Item

class Factory:

    def __init__(self, model):
        self.items = {}
        self.id_counter = 0
        self.model = model

    def get_next_id():
        obj_id = self.id_counter
        self.id_counter = self.id_counter + 1
        return obj_id

    def create_item(classnames, properties = None):
        i = self.get_next_id()
        item = Item(self.model, i, classnames, properties)
        item.validate()
        self.items[i] = item

    def __iter__(self):
        for idx in range(self.id_counter):
            yield self.items[idx]

