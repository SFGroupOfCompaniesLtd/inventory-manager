odoo.define('inventory_stock_movement.dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');

var StockMovementDashboard = AbstractAction.extend({
    template: 'StockMovementDashboard',
    events: {
        'click .o_stock_movement_dashboard_action': '_onDashboardActionClicked',
    },

    init: function(parent, action) {
        this._super.apply(this, arguments);
        this.dashboardData = {};
    },

    willStart: function() {
        var self = this;
        return $.when(
            this._super.apply(this, arguments),
            this._fetchDashboardData()
        );
    },

    start: function() {
        this._renderDashboard();
        return this._super.apply(this, arguments);
    },

    _fetchDashboardData: function() {
        var self = this;
        return rpc.query({
            route: '/inventory/stock_movement/data',
            params: {},
        }).then(function(result) {
            self.dashboardData = result;
        });
    },

    _renderDashboard: function() {
        this.$('.o_stock_movement_dashboard').html(
            QWeb.render('StockMovementDashboardContent', {
                widget: this,
                data: this.dashboardData,
            })
        );
    },

    _onDashboardActionClicked: function(e) {
        e.preventDefault();
        var action = $(e.currentTarget).attr('data-action');
        this.do_action(action);
    },

    reload: function() {
        var self = this;
        return this._fetchDashboardData().then(function() {
            self._renderDashboard();
        });
    },
});

core.action_registry.add('stock_movement_dashboard', StockMovementDashboard);

return StockMovementDashboard;

});