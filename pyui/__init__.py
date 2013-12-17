# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml.etree import tostring
from lxml.builder import E

from openerp.osv.fields import field_to_dict
from openerp.osv.orm import setup_modifiers
from openerp.tools.misc import flatten

class ViewManager(object):
    def __init__(self, model):
        assert not hasattr(model, 'PYUI_VIEW_MANAGER')
        self.model = model
        self.model.PYUI_VIEW_MANAGER = self
        def fields_view_get_wrapper(self, *args, **kwargs):
            return self.PYUI_VIEW_MANAGER.fields_view_get(self, *args, **kwargs)
        self.model.fields_view_get = fields_view_get_wrapper

    def get_tree_view(self):
        return None

    def get_form_view(self):
        return None

    def fields_view_get(self, model_inst, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(self.model, model_inst).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        view_gen_meth = {
            'tree': self.get_tree_view,
            'form': self.get_form_view,
        }.get(view_type)
        if view_gen_meth is not None:
            view = view_gen_meth()
            if view is not None:
                result['fields'] = view.field_defs(model_inst, cr, uid)
                result['arch'] = tostring(view.render())
        return result

class FieldRef(object):
    """Reference to a field.

    This can be used everywhere we expect a field name. Use this class to attach attributes to your
    field reference. This is akin to adding additional attributes to your ``<field>`` tag in XML.
    """
    def __init__(self, name, inner=None, **attrs):
        self.name = name
        self.inner = inner
        self.attrs = attrs

    def dependencies(self):
        if 'attrs' in self.attrs:
            domains = [domain for domains in self.attrs['attrs'].values() for domain in domains]
            # now we have a list of all flattened ('fieldname', '=', 'whatever') tuples
            fieldnames = [t[0] for t in domains]
            return [FieldRef(fieldname) for fieldname in fieldnames]
        else:
            return []

    def field_def(self, model, cr, uid):
        col = model._columns[self.name]
        result = field_to_dict(model, cr, uid, col)
        if self.inner is not None:
            inner_model = model.pool.get(col._obj)
            fields = self.inner.field_defs(inner_model, cr, uid)
            arch = tostring(self.inner.render())
            result['views'] = {'tree': {'fields': fields, 'arch': arch}}
        return result

    def render(self):
        # We allow the caller to supply "attrs" directly with a dict instead of a string repr of a
        # dict. It's more elegant this way and allows us easier inspection. But we have to convert
        # it to string before passing it out to lxml. 
        attrs = self.attrs
        if 'attrs' in self.attrs:
            attrs = attrs.copy()
            attrs['attrs'] = unicode(attrs['attrs'])
        node = E.field(name=self.name, **attrs)
        setup_modifiers(node)
        return node

def ensure_fieldref(name_or_ref):
    if isinstance(name_or_ref, FieldRef):
        return name_or_ref
    return FieldRef(name_or_ref)

class BaseView(object):
    def _get_all_fields(self):
        raise NotImplementedError()

    def _extra_fields(self, **attrs):
        """Returns a list of "extra" fields needed by the UI.

        The "extra" fields are thos fields that aren't displayed in the UI but that are used by
        the various "domains" tuples all around. If they aren't there, the UI will crap out, so we
        need to identify them and add them.

        If you specify extra arguments, such as "invisible", they will be injected in the fields
        you get back in the results.
        """
        result = set()
        allfields = self._get_all_fields()
        fieldnames = {field.name for field in allfields}
        for field in allfields:
            for dep in field.dependencies():
                if dep.name not in fieldnames:
                    dep.attrs = attrs
                    fieldnames.add(dep.name)
                    result.add(dep)
        return result

    def field_defs(self, model, cr, uid):
        allfields = self._get_all_fields() + list(self._extra_fields())
        return {field.name: field.field_def(model, cr, uid) for field in allfields}

class TreeView(BaseView):
    def __init__(self, title, columns, editable=None):
        self.title = title
        self.editable = editable
        self.columns = map(ensure_fieldref, columns)

    def _get_all_fields(self):
        return self.columns[:]

    def render(self):
        fields = [field.render() for field in self.columns]
        fields.extend(self._extra_fields(invisible='1'))
        attrs = dict(title=self.title)
        if self.editable:
            attrs['editable'] = self.editable
        tree = E.tree(*fields, **attrs)
        return tree

class FormView(BaseView):
    def __init__(self, title):
        self.title = title
        self.groups = []

    def _get_all_fields(self):
        return flatten(self.groups)

    def add_group(self, *fields):
        self.groups.append(map(ensure_fieldref, fields))

    def render(self):
        def render_group(fields):
            return E.group(*[field.render() for field in fields])
        groups = [render_group(fields) for fields in self.groups]
        groups.extend(f.render() for f in self._extra_fields(invisible='1'))
        form = E.form(E.sheet(*groups), title=self.title)
        return form

