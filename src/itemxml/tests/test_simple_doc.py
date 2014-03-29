from os import path
from StringIO import StringIO
from contextlib import closing

import intermine.model

from itemxml.document import Factory
from itemxml.io import XMLWriter

import unittest

model_file = path.join(path.dirname(__file__), '..', '..', '..', 'resources', 'testmodel_model.xml')
expected_result = path.join(path.dirname(__file__), '..', '..', '..', 'resources', 'simple-document.xml')

class SimpleDocumentTestCase(unittest.TestCase):

    def setUp(self):
        model = intermine.model.Model(model_file)
        self.items = Factory(model)

    def test_document(self):

        deps = map(lambda c: self.items.add('Department', name = c), ["Big", "Small"])
        for idx, name in enumerate(["Tom", "Dick", "Harry"]):
            e = self.items.add('Employee', name = name)
            e.set('department', deps[idx % 2])
            e.set('age', idx + 25)
        c = self.items.add('Company', name = "UberCorp", departments = deps)

        with closing(open(expected_result)) as f:
            expected = f.read()

        with closing(StringIO()) as buff, XMLWriter(buff) as writer:
            writer.write_items(self.items)
            result = buff.getvalue()

        self.assertEqual(result, expected)

def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(SimpleDocumentTestCase))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())

