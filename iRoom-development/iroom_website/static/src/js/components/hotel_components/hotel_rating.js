/** @odoo-module **/

import PublicWidget from '@web/legacy/js/public/public_widget';

PublicWidget.registry.HotelRating = PublicWidget.Widget.extend({
    selector: '#add-comment',

    events: {
        'click #add-comment-btn': '_onSubmit'
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    _onSubmit: async function(event) {
        debugger;
        event.preventDefault();

        const rateElements = document.getElementsByName('rgcl');
        const name = document.getElementById('rater-name').value;
        const email = document.getElementById('rater-email').value;
        const description = document.getElementById('rating-description').value;

        const data = {
            cleanliness: Number(rateElements[0].value),
            comfort: Number(rateElements[1].value),
            staff: Number(rateElements[2].value),
            facilities_and_services: Number(rateElements[3].value),
            name,
            email,
            description
        };

        await this.rpc('/create_rating', data);
        location.reload();
    }
});
