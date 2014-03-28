import itemxml
import test_simple_doc

def suite():
    import unittest
    import doctest
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(itemxml.document))
    suite.addTests(test_simple_doc.suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

