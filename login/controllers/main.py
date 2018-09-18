# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo Web Login Screen
#    Copyright (C) 2016- XUBI.ME (http://www.xubi.me)
#    @author binhnguyenxuan
#    (https://www.linkedin.com/in/binh-nguyen-xuan-46556279)

from ast import literal_eval

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

import datetime
import pytz
from pytz import timezone


class LoginHome(Home):

    @staticmethod
    def get_param(parameter):
        # Just to ensure any extra parameter is read here.
        parameters = [
            'login_form_disable_footer',
            'login_form_disable_database_manager',
            'login_form_change_background_by_hour',
            'login_form_change_background_timezone',
            'login_form_background_default',
            'login_form_background_dawn',
            'login_form_background_night',
            'login_form_background_dusk',
            'login_form_background_day',
        ]
        if parameter not in parameters:
            return False
        param = request.env['ir.config_parameter'].sudo()
        get_param = param.get_param
        if 'login_form_background' in parameter or \
                parameter == 'login_form_change_background_timezone':
            return get_param(parameter) or ''
        return literal_eval(get_param(parameter) or '')

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        lfdf = self.get_param('login_form_disable_footer')
        lfddm = self.get_param('login_form_disable_database_manager')
        change = self.get_param('login_form_change_background_by_hour')
        request.params['disable_footer'] = lfdf or False
        request.params['disable_database_manager'] = lfddm or False
        background = self.get_param('login_form_background_default')
        request.params['background_src'] = background
        if not change:
            return super(LoginHome, self).web_login(redirect, **kw)
        clt = self.get_param('login_form_change_background_timezone')
        dawn = self.get_param('login_form_background_dawn')
        night = self.get_param('login_form_background_night')
        day = self.get_param('login_form_background_day')
        dusk = self.get_param('login_form_background_dusk')
        tz = timezone(clt) if clt else pytz.utc
        current_hour = datetime.datetime.now(tz=tz).hour
        if 3 > current_hour >= 0 or 24 > current_hour >= 18:
            background = night
        elif 7 > current_hour >= 3:
            background = dawn
        elif 16 > current_hour >= 7:
            background = day
        else:
            background = dusk
        request.params['background_src'] = background
        return super(LoginHome, self).web_login(redirect, **kw)


class LoginAuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        param_obj = request.env['ir.config_parameter'].sudo()
        df = param_obj.get_param('login_form_disable_footer')
        request.params['disable_footer'] = df
        return super(LoginAuthSignupHome, self).web_auth_signup(*args, **kw)

    @http.route('/web/reset_password', type='http', auth='public',
                website=True)
    def web_auth_reset_password(self, *args, **kw):
        param_obj = request.env['ir.config_parameter'].sudo()
        df = param_obj.get_param('login_form_disable_footer')
        request.params['disable_footer'] = df
        return super(LoginAuthSignupHome, self).web_auth_reset_password(
            *args, **kw)
