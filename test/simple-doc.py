import sys, os, random

sys.path.append(os.path.dirname(__file__) + "/..")

import intermine.model
from itemxml import document, io

model = intermine.model.Model(os.path.dirname(__file__) + "/../resources/testmodel_model.xml")

print(model.get_class("Employee").is_interface)

items = document.Factory(model)

deps = map(lambda c: items.add(["Department"], {"name": c}), ["Big", "Small"])

for name in ["Tom", "Dick", "Harry"]:
    e = items.add(["Employee"], {"name": name})
    e.set('department', random.choice(deps))
    e.set('age', random.randint(25, 65))

c = items.add(["Company"], {"name": "UberCorp", "departments": deps})

print(items.get(0))

print(list(items.search("Employee", {"name": "Tom"})))

io.write_itemsxml(items)

