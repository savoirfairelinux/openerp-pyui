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

from pyui import TreeView, FormView, ViewManager, FieldRef

class simplenote_note(orm.Model):
    _name = 'simplenote.note'

    _columns = {
        'sequence': fields.integer("Sequence", required=True),
        'title': fields.char("Title", size=200),
        'subject': fields.char("Subject", size=200),
        'note': fields.char("Note", size=2000),
        'tag_ids': fields.one2many('simplenote.tag', 'note_id', "Tags"),
    }
    _defaults = {
        'sequence': 0,
    }
    _order = 'sequence'

class SimpleNoteViewManager(ViewManager):
    def get_tree_view(self):
        columns = [
            FieldRef('sequence', widget='handle'),
            'title',
            'subject',
        ]
        return TreeView("Simple notes", columns=columns)

    def get_form_view(self):
        view = FormView("Simple note")
        tag_tree = TreeView("", columns=['label'], editable='bottom')
        fields = [
            'title',
            FieldRef('subject', attrs={'readonly': [('title', '=', 'foobar')]}),
            'note',
            FieldRef('tag_ids', inner=tag_tree),
        ]
        view.add_group(*fields)
        return view


# We have to instantiate a ViewManager to make it "wrap" its target model
SimpleNoteViewManager(simplenote_note)

class simplenote_tag(orm.Model):
    _name = 'simplenote.tag'

    _columns = {
        'note_id': fields.many2one('simplenote.note', "Note"),
        'label': fields.char("Label", size=50),
    }
