# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Compassion CH (http://www.compassion.ch)
#    Releasing children from poverty in Jesus' name
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __openerp__.py
#
##############################################################################

import logging
from openerp import models, fields, api, _

logger = logging.getLogger(__name__)


class IrAdvancedTranslation(models.Model):
    """ Used to translate terms in context of a subject that can be
    male / female and singular / plural.
    """
    _name = 'ir.advanced.translation'
    _description = 'Advanced translation terms'

    src = fields.Text(required=True, translate=False)
    lang = fields.Selection('_get_lang', required=True)
    group = fields.Char()
    male_singular = fields.Text(translate=False)
    male_plural = fields.Text(translate=False)
    female_singular = fields.Text(translate=False)
    female_plural = fields.Text(translate=False)

    _sql_constraints = [
        ('unique_term', "unique(src, lang)", "The term already exists")
    ]

    @api.model
    def _get_lang(self):
        langs = self.env['res.lang'].search([])
        return [(l.code, l.name) for l in langs]

    @api.model
    def get(self, src, female=False, plural=False):
        """ Returns the translation term. """
        term = self.search([
            ('src', '=', src),
            ('lang', '=', self.env.lang)])
        if not term:
            return _(src)
        if female and plural:
            return term.female_plural
        if female:
            return term.female_singular
        if plural:
            return term.male_plural
        return term.male_singular


class AdvancedTranslatable(models.AbstractModel):
    """ Inherit this classe in order to let your model fetch keywords
    based on the source recordset and a gender field in the model.
    """

    _name = 'advanced.translatable'

    gender = fields.Selection([
        ('M', 'Male'),
        ('F', 'Female'),
    ])

    @api.multi
    def get(self, keyword):
        plural = len(self) > 1
        male = self.filtered(lambda c: c.gender == 'M')
        female = self.filtered(lambda c: c.gender == 'F')
        advanced_translation = self.env['ir.advanced.translation']
        if plural and female and not male:
            return advanced_translation.get(keyword, True, True)
        elif plural:
            return advanced_translation.get(keyword, plural=True)
        elif female and not male:
            return advanced_translation.get(keyword, female=True)
        else:
            return advanced_translation.get(keyword)
