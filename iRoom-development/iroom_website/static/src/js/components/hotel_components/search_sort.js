/** @odoo-module **/

import PublicWidget from '@web/legacy/js/public/public_widget';

PublicWidget.registry.SearchSort = PublicWidget.Widget.extend({
    selector: 'select[name="order_by"]',

    events: {
        'change': '_onChange'
    },

    _onChange: function(event) {
        debugger;
        const orderByValue = event.target.value;
        const url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);
        params.set('page', 1);
        params.set('order_by', orderByValue);
        url.search = params.toString();
        location.href = url.toString();
    },
});
