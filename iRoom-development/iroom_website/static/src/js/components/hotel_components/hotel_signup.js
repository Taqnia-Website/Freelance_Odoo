/** @odoo-module **/

import PublicWidget from '@web/legacy/js/public/public_widget';
import { session } from "@web/session";

PublicWidget.registry.HotelSignup = PublicWidget.Widget.extend({
    selector: '#hotel-signup',

    events: {
        'click #create-reservation-btn': '_createReservation',
        'click #signup-country + div.nice-select li': '_updateStates'
    },

    init: function() {
        this._super(...arguments);
        this.rpc = this.bindService('rpc');

        this.data = {};
    },

    start: function() {
        this.getStates();
    },

    getStates: async function() {
        const states = await this.rpc('/api/get_states', {});
        this.data.states = states;
    },

    _updateStates: function(event) {
    debugger;
        const countryId = $(event.target).data('value');
        const statesSelectElement = $('#signup-state');
        const statesUlElement = $('#signup-state').siblings('div.nice-select').find('ul');
        if(!countryId) {
            statesSelectElement.html('');
            statesUlElement.html('');
        } else {
            const statesOfCountry = this.data.states.filter((state) => {
                return state.country_id == countryId;
            });
            let stateOptions = ``;
            let stateLis = ``;
            for(let state of statesOfCountry) {
                stateOptions += `<option value="${state.id}" data-countryId="${state.country_id}">${state.name}</option>`;
                stateLis += `<li data-value="${state.id}" data-countryId="${state.country_id}" class="option">${state.name}</li>`;
            }
            statesSelectElement.html(stateOptions);
            statesUlElement.html(stateLis);
        }
    },

    _createReservation: async function(event) {
        event.preventDefault();

        const room_id = Number($('[name="repopt"]').first().val());
        const [check_in, check_out] = $('[name="bookdates"]').first().val().split(' - ');
        const number_of_adults = Number($('[name="qty3"]').first().val());
        const number_of_children = Number($('[name="qty2"]').first().val());

        const first_name = $('#signup-first-name').val();
        const last_name = $('#signup-last-name').val();
        const email = $('#signup-email').val();
        const password = $('#signup-password').val();
        const mobile = $('#signup-mobile').val();
        const terms_and_conditions = $('#signup-conditions').val();

        const country_id = $('#signup-country').val();
        const state_id = $('#signup-state').val();
        const city = $('#signup-city').val();
        const region = $('#signup-region').val();
        const zip = $('#signup-zipCode').val();
        const comment = $('#signup-notes').val();

        const card_owner = $('#signup-card-owner').val();
        const card_number = $('#signup-card-number').val();
        const card_month = $('#signup-card-month').val();
        const card_cvv_cvc = $('#signup-cvv-cvc').val();

        debugger;
        const reservationResponse = await this.rpc('/api/create_reservation', {
            user_id: session.user_id, room_id, check_in, check_out, number_of_adults, number_of_children,
            first_name, last_name, email, password, mobile, terms_and_conditions,
            country_id, state_id, city, region, zip, comment,
            card_owner, card_number, card_month, card_cvv_cvc
        });

        if(reservationResponse.error) {
            $('#signup-error').empty();
            let message = `<ul id="signup-error">`;
            for(const error of reservationResponse.message)
                message += `<li style="color:red">${error}</li>`;
            message += `</ul`;
            $('#signup-error').html(message);
            $('fieldset.book_mdf').each(function() {
                $(this).removeAttr('style');
            });
            $('fieldset.book_mdf').eq(2).hide();
            $('#progressbar li').eq(2).removeClass('active');
            $('#progressbar li').eq(1).removeClass('active');
            $('fieldset.book_mdf').eq(0).show().css({
                'transform': 'scale(1)',
                'position': 'relative',
                'opacity': '1'
            });
        }

//        const creationResponse = await this.rpc('/api/create_user', {
//            name, email, password, mobile, country_id, state_id, city, region, zip, comment
//        });
//
//        if(creationResponse.error) {
//            $('#signup-error').empty();
//            let message = `<ul id="signup-error">`;
//            for(const error of creationResponse.message)
//                message += `<li style="color:red">${error}</li>`;
//            message += `</ul`;
//            $('#signup-error').html(message);
//        }
//
//        if(creationResponse.signup) {
//            const updatePasswordResponse = await this.rpc('/api/update_user_password', {
//                user_id: creationResponse.user_id,
//                password: creationResponse.password
//            });
//            if(updatePasswordResponse) location.href = '/web/login';
//            else location.reload();
//        }
    }
});
