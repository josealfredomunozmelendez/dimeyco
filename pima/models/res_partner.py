# coding: utf-8
from odoo import models, api
import werkzeug


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def google_map_img(self, zoom=14, width=640, height=405):
        partner = self
        address = '%s %s, %s, %s, %s' % (
                partner.street_name or '',
                partner.street_number or '',
                partner.city or '',
                partner.zip or '',
                partner.country_id and partner.country_id.name_get()[0][1] or ''),  # noqa
        params = {
            'center': address,
            'size': "%sx%s" % (width, height),
            'zoom': zoom,
            'markers': address,
            'scale': 2,
        }
        return urlplus('//maps.googleapis.com/maps/api/staticmap', params)
