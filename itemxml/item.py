ID_PREFIX = '0_'

import intermine

class ItemTypeError(Exception):
    pass

class NoTypeError(ItemTypeError):

    MSG = "Item declared with neither class-name nor set of interfaces"

    def __init__(self):
        ItemTypeError.__init__(self, NoTypeError.MSG)

class ItemPropertyError(Exception):
    MSG = "This value (%s) is not suitable for this field (%s)"

    def __init__(self, value, field):
        Exception.__init__(self, ItemPropertyError.MSG % (value, field))

class Item:

    def __init__(self, model, item_id, classnames = None, properties = None):
        if properties is None:
            properties = {}

        if classnames is None:
            classnames = set()
        else:
            classnames = set(classnames)

        self.model = model
        self.classnames = classnames
        self.properties = properties
        self.properties['id'] = item_id
        self.classes = set()
        self.fields = {}

    def __str__(self):
        return "<Item classes=%s, properties=%s>" % (self.classnames, self.properties)

    def __repr__(self):
        return "Item(%s, %s, %s)" % (self.get('id'), self.classnames, self.properties)

    @property
    def classname(self):
        if len(self.classes) == 1:
            c = next(iter(self.classes))
            if not c.is_interface:
                return c.name
        return None

    @property
    def implements(self):
        if len(self.classes) == 1:
            c = next(iter(self.classes))
            if not c.is_interface:
                return set()
        return self.classnames

    def validate(self):
        self.validate_type()
        self.validate_properties()

    def validate_type(self):
        """ Make sure this item is typed properly, and resolve the set of
            class-descriptors it refers to """
        if len(self.classnames):
            for name in self.classnames:
                self.classes.add(self.model.get_class(name))
        else:
            raise NoTypeError()

        self.fields = dict(reduce(lambda x, y: y.field_dict.items() + x, self.classes, []))

    def get_field_descriptor(self, name):
        if name in self.fields:
            return self.fields[name]
        raise ItemTypeError("Could not find field %s in %s with fields: %s" % (name, self.classes, self.fields.keys()))

    def validate_properties(self):
        for name, value in self.properties.items():
            self.validate_property(name, value)

    def validate_property(self, name, value):
        fd = self.get_field_descriptor(name)
        if fd.type_class is not None:
            if fd.fieldtype == "collection":
                try:
                    for item in value:
                        if not item.is_assignable_to(fd):
                            raise ItemPropertyError(item, fd)
                except TypeError:
                    raise ItemPropertyError(value, fd)
            elif not value.is_assignable_to(fd):
                raise ItemPropertyError(value, fd)
        elif isinstance(value, Item):
            raise ItemPropertyError(value, fd)
        else: ## Don't try to check attribute properties - it's not worth it.
            pass

    def is_assignable_to(self, field):
        if field.type_class is None:
            return False
        else:
            for cd in self.classes:
                if cd.isa(field.type_class):
                    return True
        return False

    def set(self, name, value):
        self.validate_property(name, value)
        self.properties[name] = value

    def get(self, name):
        self.get_field_descriptor(name) # Check it can exist.
        return self.properties[name]

