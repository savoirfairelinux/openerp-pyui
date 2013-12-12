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
                result['fields'] = view.field_defs(self.model, cr, uid)
                result['arch'] = view.render()
        return result

class BaseView(object):
    def _get_all_fieldnames(self):
        raise NotImplementedError()

    def field_defs(self, model, cr, uid):
        res = {}
        for fieldname in self._get_all_fieldnames():
            col = model._columns[fieldname]
            res[fieldname] = field_to_dict(model, cr, uid, col)
        return res
    
class TreeView(BaseView):
    def __init__(self, title, columns):
        self.title = title
        self.columns = columns

    def _get_all_fieldnames(self):
        return self.columns

    def render(self):
        fields = [E.field(name=col) for col in self.columns]
        tree = E.tree(*fields, title=self.title)
        return tostring(tree)

class FormView(BaseView):
    def __init__(self, title):
        self.title = title
        self.groups = []

    def _get_all_fieldnames(self):
        return flatten(self.groups)

    def add_group(self, *fieldnames):
        self.groups.append(fieldnames)

    def render(self):
        def render_group(fieldnames):
            fields = [E.field(name=fieldname) for fieldname in fieldnames]
            return E.group(*fields)
        groups = [render_group(fieldnames) for fieldnames in self.groups]
        form = E.form(E.sheet(*groups), title=self.title)
        return tostring(form)

