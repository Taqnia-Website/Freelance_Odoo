/** @odoo-module **/

import PublicWidget from '@web/legacy/js/public/public_widget';

PublicWidget.registry.HotelReservationCard = PublicWidget.Widget.extend({
    selector: 'form[name="bookFormCalc"]',

    events: {
        'click #hotel-reservation-card-submit': '_openSignup',
        'change #hotel-reservation-card-room-type': '_onInputsChange',
        'change #hotel-reservation-card-date-range': '_onInputsChange',
        'click .applyBtn': '_onInputsChange'
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
    },

    _openSignup: async function(event) {
        const roomId = Number($('[name="repopt"]').first().val());
        const dateRange = $('[name="bookdates"]').first().val();
        const numberOfAdults = Number($('[name="qty3"]').first().val());
        const numberOfChildren = Number($('[name="qty2"]').first().val());

        const reservationWarningElement = $('#reservation-warning');

        if(roomId && dateRange && (numberOfAdults || numberOfChildren)) {
            reservationWarningElement.addClass('d-none');
            const [checkIn, checkOut] = dateRange.split(' - ');
            const data = {
                room_id: roomId,
                check_in: checkIn,
                check_out: checkOut,
                adult_number: numberOfAdults,
                children_number: numberOfChildren
            }
            const response = await this.rpc('/api/check_reservation', data);
            if(response.error) {
                $('.booking-modal-wrap').hide();
                $('.bmw-overlay').hide();
                reservationWarningElement.html(response.message);
                reservationWarningElement.removeClass('d-none');
            }
        } else {
            $('.booking-modal-wrap').hide();
            $('.bmw-overlay').hide();
            reservationWarningElement.html('You need to fill reservation data');
            reservationWarningElement.removeClass('d-none');
        }
    },

//    _openSignup: async function(event) {
//        debugger;
//        const bookingRoomElement = document.getElementsByName('repopt')[0];
//        const bookingRoomId = Number(bookingRoomElement.value);
//        const selectedIndex = bookingRoomElement.selectedIndex;
//        const selectedOption = bookingRoomElement.options[selectedIndex];
//        const bookingRoomName = selectedOption.dataset.name;
//
//        const bookingDateRangeElement = document.getElementsByName('bookdates')[0];
//        const bookingDateRange = bookingDateRangeElement.value;
//
//        const bookingAdultNumberElement = document.getElementsByName('qty3')[0];
//        const bookingAdultNumber = Number(bookingAdultNumberElement.value);
//
//        const bookingChildrenNumberElement = document.getElementsByName('qty2')[0];
//        const bookingChildrenNumber = Number(bookingChildrenNumberElement.value);
//
//        if(bookingRoomId && bookingDateRange && bookingAdultNumber && bookingChildrenNumber) {
//            const [checkIn, checkOut] = bookingDateRange.split(' - ');
//            const data = {
//                room_id: bookingRoomId,
//                check_in: checkIn,
//                check_out: checkOut,
//                adult_number: bookingAdultNumber,
//                children_number: bookingChildrenNumber
//            }
//            const response = await this.rpc('/api/check_reservation', data);
//            if(!response.error) {
//                debugger;
//                const clientName = $('form#hotel-signup[name="client-first-name"]').val();
//
////                    const productLink = `/shop/${bookingRoomName}-${bookingRoomId}?room_id=${bookingRoomId}&reservation_from=${checkIn}&reservation_to=${checkOut}&number_of_adults=${bookingAdultNumber}&number_of_children=${bookingChildrenNumber}`;
////                    location.href = productLink;
//            } else {
//                const reservationWarningElement = document.getElementById('reservation-warning');
//                reservationWarningElement.innerHTML = response.message;
//                reservationWarningElement.classList.remove('d-none');
//            }
////                const data = {
////                    room_type_id: bookingRoomId,
////                    check_in: checkIn,
////                    check_out: checkOut,
////                    adult_number: bookingAdultNumber,
////                    children_number: bookingChildrenNumber,
////                    user_id: session.user_id
////                }
////                const response = await this.rpc('/create_reservation', data);
////                if(response.error) {
////                    const reservationWarningElement = document.getElementById('reservation-warning');
////                    reservationWarningElement.innerHTML = response.message;
////                    reservationWarningElement.classList.remove('d-none');
////                }
////                if(response.success)
////                    location.href = response.redirect_to
//
//        } else {
//            $('.booking-modal-wrap').hide();
//            $('.bmw-overlay').hide();
//        }
//    },

    _onInputsChange: function(event) {
        const bookingRoomTypeElement = document.getElementsByName('repopt')[0];
        const currency = bookingRoomTypeElement.selectedOptions[0].dataset.currency;

        const currencyElement = document.getElementsByName('grand_total_currency')[0];
        currencyElement.innerHTML = currency ? currency : 'SAR';

        if(bookingRoomTypeElement.selectedOptions[0].dataset.unitprice) {
            const bookingDateRangeElement = document.getElementsByName('bookdates')[0];
            const bookingDateRange = bookingDateRangeElement.value;
            if(bookingDateRange) {
                let [checkIn, checkOut] = bookingDateRange.split(' - ');
                checkIn = new Date(checkIn);
                checkOut = new Date(checkOut);
                const difference = (checkOut - checkIn) / (24 * 60 * 60 * 1000); // Convert milliseconds to days
                const unitPrice = Number(bookingRoomTypeElement.selectedOptions[0].dataset.unitprice);
                const totalElement = document.getElementsByName('grand_total')[0];
                totalElement.value = unitPrice * difference;
            }
        }
    }
});
