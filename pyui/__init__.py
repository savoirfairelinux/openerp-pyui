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

    def fields_view_get(self, model_inst, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(self.model, model_inst).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if view_type == 'tree':
            view = self.get_tree_view()
            if view is not None:
                result['fields'] = view.field_defs(self.model, cr, uid)
                result['arch'] = view.render()
        return result

class TreeView(object):
    def __init__(self, title, columns):
        self.title = title
        self.columns = columns

    def field_defs(self, model, cr, uid):
        res = {}
        for colname in self.columns:
            col = model._columns[colname]
            res[colname] = field_to_dict(model, cr, uid, col)
        return res

    def render(self):
        fields = [E.field(name=col) for col in self.columns]
        tree = E.tree(*fields, title=self.title)
        return tostring(tree)
