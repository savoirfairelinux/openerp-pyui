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
