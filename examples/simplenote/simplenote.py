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

from openerp.osv import orm, fields

from pyui import TreeView

class simplenote_note(orm.Model):
    _name = 'simplenote.note'

    _columns = {
        'title': fields.char("Title", size=200),
        'subject': fields.char("Subject", size=200),
        'note': fields.char("Note", size=2000),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(simplenote_note, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if view_type == 'tree':
            view = TreeView(self, "Simple notes", columns=['title', 'subject'])
            result['arch'] = view.render()
        return result

