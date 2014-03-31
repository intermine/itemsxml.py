ID_PREFIX = '0_'

def get_model():
    from os.path import join, dirname
    import intermine.model
    return intermine.model.Model(join(dirname(__file__), '..', '..', 'resources', 'testmodel_model.xml'))

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
    """A record to be written into an InterMine DB, and merged with others.

    >>> item = Item(get_model(), 1, ['Employee', 'Broke'], {'name': 'John', 'debt': 100})
    >>> print item
    <Item classes=set(['Employee', 'Broke']), properties={'debt': 100, 'name': 'John', 'id': 1}>
    """

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
        self._classes = None
        self._fields = None

    def set(self, name, value):
        """Add a datum to this item.

        >>> schema = get_model()
        >>> item = Item(schema, 1, ['Employee', 'Broke'], {'name': 'Brian'})
        >>> item.set('debt', 200)
        >>> print item
        <Item classes=set(['Employee', 'Broke']), properties={'debt': 200, 'name': 'Brian', 'id': 1}>

        Only valid data is allowed. Invalid property assignment will
        raise errors.

        >>> item.set('perversity', float('inf'))
        Traceback (most recent call last):
        ...
        ItemTypeError: Could not find field perversity...

        Illegal access will not change the item:
        >>> print item
        <Item classes=set(['Employee', 'Broke']), properties={'debt': 200, 'name': 'Brian', 'id': 1}>
        """
        fd = self.validate_property(name, value)
        if fd.fieldtype == 'collection':
            self.properties[name] = set(value)
        else:
            self.properties[name] = value

    def get(self, name):
        """Get a datum from this item.

        >>> item = Item(get_model(), 1, ['Employee', 'Broke'], {'name': 'Susan'})
        >>> print item.get('name')
        Susan

        Accessing unset properties is valid, but they must conform to
        the data model
        >>> print item.get('debt')
        None

        Accessing properties that don't conform with the data model
        will cause an error to be raised
        >>> print item.get('perversity')
        Traceback (most recent call last):
        ...
        ItemTypeError: Could not find field perversity...
        """
        fd = self.get_field_descriptor(name) # Check it can exist.
        val = self.properties.get(name)
        if not val and fd.fieldtype == 'collection':
            return set()
        else:
            return val

    def __str__(self):
        return "<Item classes=%r, properties=%r>" % (self.classnames, self.properties)

    def __repr__(self):
        return "Item(%s, %s, %s)" % (self.get('id'), self.classnames, self.properties)

    @property
    def classes(self):
        if self._classes is None:
            self._classes = set()
            for name in self.classnames:
                self.classes.add(self.model.get_class(name))
        return self._classes

    @property
    def fields(self):
        if self._fields is None:
            self._fields = dict(reduce(lambda x, y: y.field_dict.items() + x, self.classes, []))
        return self._fields

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
        """Check that this item is valid, throwing an error if not.

        >>> schema = get_model()
        >>> good = Item(schema, 1, ['Employee', 'Broke'], {'name': 'John', 'debt': 100})
        >>> good.validate()
        >>> bad = Item(schema, 1, ['Employee'], {'name': 'John', 'debt': 100})
        >>> bad.validate()
        Traceback (most recent call last):
        ...
        ItemTypeError: Could not find field debt...
        >>> terrible = Item(schema, 1, ['Foo'], {'name': 'John', 'debt': 100})
        >>> terrible.validate()
        Traceback (most recent call last):
        ...
        ModelError: "'Foo' is not a class in this model"
        """
        self.validate_type()
        self.validate_properties()

    def validate_type(self):
        """ Make sure this item is typed properly, and resolve the set of
            class-descriptors it refers to

        >>> schema = get_model()
        >>> terrible = Item(schema, 1, ['Foo'], {'name': 'John', 'debt': 100})
        >>> terrible.validate_type()
        Traceback (most recent call last):
        ...
        ModelError: "'Foo' is not a class in this model"
        >>> woeful = Item(schema, 1, [], {'name': 'John', 'debt': 100})
        >>> woeful.validate_type()
        Traceback (most recent call last):
        ...
        NoTypeError: "Item declared with neither class-name nor set of interfaces"
        """
        if not len(self.classes):
            raise NoTypeError()

    def get_field_descriptor(self, name):
        if name in self.fields:
            return self.fields[name]
        raise ItemTypeError("Could not find field %s in %s with fields: %s" % (name, self.classes, self.fields.keys()))

    def validate_properties(self):
        for name, value in self.properties.items():
            self.validate_property(name, value)

    def add_to(self, collection, *members):
        """Add one or more members to a collection.

        If the collection is not a property of this item,
        or the members are of the wrong type, an error
        will be raised, prior to modification of the item
        itself.

        >>> schema = get_model()
        >>> dep = Item(schema, 1, ['Department'], {'name': 'Sales'})
        >>> boss = Item(schema, 3, ['Manager'], {'name': 'boss'})
        >>> worker_1 = Item(schema, 2, ['Employee'], {'name': 'worker_1'})
        >>> worker_2 = Item(schema, 2, ['Employee'], {'name': 'worker_2'})
        >>> dep.add_to('employees', boss)
        >>> dep.add_to('employees', worker_1, worker_2)
        >>> print len(dep.get('employees'))
        3
        >>> print boss in dep.get('employees')
        True
        """
        self.validate_property(collection, members)
        if not self.get(collection):
            self.set(collection, members)
        else:
            self.get(collection).update(members)

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
        return fd

    def is_assignable_to(self, field):
        if field.type_class is None:
            return False
        else:
            for cd in self.classes:
                if cd.isa(field.type_class):
                    return True
        return False
