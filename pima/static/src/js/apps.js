odoo.define('theme_pima.apps', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');
    var Widget = require('web.Widget');

    var qweb = core.qweb;
    var _t = core._t;

    if(!$('.app-check').length) {
        return $.Deferred().reject("DOM doesn't contain a app button check");
    }
    ajax.loadXML('/web/static/src/xml/base_common.xml', qweb).then(function () {
        ajax.loadXML('/pima/static/src/xml/apps.xml', qweb);
    });
    /**
    Rendered on server side but widget generated in client side.
    */
    var App = Widget.extend({
        events: {
            'click .app-check' : 'onClick',
        },
        init: function(parent){
            this._super(parent);
        },
        start: function(){
            return this._super.apply(this, arguments);
        },
        onClick: function(){
            var input = this.$('.app-check');
            var values = input.data();
            var added = $(qweb.render("pima.apps_selected", values)).appendTo(".js_apps_selected_placeholder");
        }
    });
    var Order = Widget.extend({
        events: {
            'click #quick-or-premise' : 'onClick',
        },
        init: function(parent){
            this._super(parent);
        },
        start: function(){
            return this._super.apply(this, arguments);
        },
        onClick: function(){
            var input = this.$('.app-check');
        }
    });

    var button_list = [];
    $('.app').each(function( index ) {
        var button = new App();
        button.setElement($(this)).start();
        button_list.push(button);
    });
    $('#on_premise_apps').ready(function() {
        new Order($(this)).setElement($('.apps-tray'));
    });
});
