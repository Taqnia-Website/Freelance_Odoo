/** @odoo-module **/

import PublicWidget from '@web/legacy/js/public/public_widget';

PublicWidget.registry.HotelRoomDetails = PublicWidget.Widget.extend({
    selector: '.rooms-container',

    events: {
//        'click #hotel-room-details-btn': '_onClick'
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    _onClick: async function(event) {
        debugger;
//        const roomId = event.
//        const room = await this.rpc('/api/get_room_by_id', data);
    }
});
