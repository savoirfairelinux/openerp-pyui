OpenERP PyUI: Say no to XML madness!
===

PyUI is a Python library made to let OpenERP developers design their views in their Python code
rather than having to write confusing XML. For example, one could write this tree view:

```xml
<record id="foobar_list_view" model="ir.ui.view">
    <field name="name">My Foobar List</field>
    <field name="model">foobar.foobar</field>
    <field name="arch" type="xml">
        <tree string="Foobars">
            <field name="name"/>
            <field name="field1"/>
            <field name="field2"/>
        </tree>
    </field>
</record>
```

by writing this instead:

```python
from openerp.osv import orm, fields
from pyui import TreeView

class foobar_foobar(orm.Model):
    _name = 'foobar.foobar'
    # [...]
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(foobar_foobar, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if view_type == 'tree':
            view = TreeView(self, "My Foobar List", columns=['name', 'field1', 'field2'])
            result['arch'] = view.render()
        return result
```

Installation
---

Clone this repo and run:

    python setup.py install

This will install a new ``pyui`` module which you can then import in your OpenERP modules.

How it works
---

OpenERP stores its UI in a ... "battle-scarred" XML format, which is sent to its Javascript web
interface for parsing and UI generation. This XML format is so central to OpenERP that we can't
really get rid of it, but what we can do is make the life of the poor developer easier by
abstracting this XML generation away in a much nicer API.

This is done by overriding ``fields_view_get``, which is called by the JS UI whenever it needs a
view. We then dynamically set the ``arch`` part of the result by creating and rendering wrappers
supplied by this awesome PyUI library.

Compatibility warning
---

It's important to realize that this approach is incompatible with OpenERP XML inheritance model.
When we want to inherit from a view, we refer to it by its "record id", which we don't have with
a Python UI because it doesn't live in the DB.

Inheritance (when we figure out how it will work in the PyUI world) will have to be done exclusively
in the PyUI world.

Alpha status
---

This library is in its infancy and we're still thinking the API as we go, so it's very probably
going to change a lot before it stabilize.

Examples
---

The ``examples`` folder contains demo OpenERP modules using PyUI. You can add this folder to your
addons list and install the modules to try them.
