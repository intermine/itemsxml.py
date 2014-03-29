Python implementation of Item-XML format writer.
==================================================

This is a library for generating valid items xml from python
code.

Usage
-------

```: python
from contextlib import closing
from intermine.model import Model
from itemxml import document, io

gene_file = 'path/to/gene_list.txt'
model = Model("path/to/model.xml")
document = document.Factory(model)

organism = document.add(['Organism'], taxonId = 7227)

with closing(open(gene_file)) as genes, io.XMLWriter() as w:
    w.write_item(organism)
    for line in genes:
        if not line.startswith("#"):
            gene = document.add(['Gene'], symbol = line)
            gene.set('organism', organism)
            w.write_item(gene)
```

This library is designed to support writing items incrementally
to an output stream. To do this queue items up in a document and
periodically write them out when they are complete, meaning that
we don't need to hold the whole data set in memory.

Copyright and License
-----------------------

Copyright © InterMine 2013-2014
This software is free and open source software under the
[LGPL.](LICENSE)

