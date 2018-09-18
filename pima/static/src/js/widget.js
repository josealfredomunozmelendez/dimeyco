odoo.define('pima.widgets', function (require) {
"use strict";
var registry = require('web.field_registry');
var basic_fields = require('web.basic_fields');
var core = require('web.core');

var _t = core._t;

var SetWidget = basic_fields.FavoriteWidget.extend({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Render set widget icon based on state
     *
     * @override
     * @private
     */
    _render: function () {
        console.log(this);
        var template = this.attrs.nolabel ? '<a href="#"><i class="fa %s" title="%s"></i></a>' : '<a href="#"><i class="fa %s"></i> %s</a>';
        this.$el.empty().append(_.str.sprintf(template, this.value ? 'fa-star' : 'fa-star-o', this.value ? this.string : this.string));
    }
});

registry.add('set_widget', SetWidget);

return {
    SetWidget: SetWidget
}
});
