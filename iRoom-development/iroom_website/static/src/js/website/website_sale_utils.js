/** @odoo-module **/

import { WebsiteSale } from '@website_sale/js/website_sale';
import publicWidget from '@web/legacy/js/public/public_widget';

const CustomWebsiteSale = WebsiteSale.extend({
    _submitForm: function () {
        const params = this.rootProduct;

        const $product = $('#product_detail');
        const productTrackingInfo = $product.data('product-tracking-info');
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger('add_to_cart_event', [productTrackingInfo]);
        }

        params.add_qty = params.quantity;
        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        delete params.quantity;

        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const room_id = Number(urlParams.get('room_id'));
        const reservation_from = urlParams.get('reservation_from');
        const reservation_to = urlParams.get('reservation_to');
        const number_of_adults = Number(urlParams.get('number_of_adults'));
        const number_of_children = Number(urlParams.get('number_of_children'));

        const customParams = {
            ...params,
            room_id, reservation_from, reservation_to, number_of_adults, number_of_children
        }
        return this.addToCart(customParams);
    }
});
publicWidget.registry.WebsiteSale = CustomWebsiteSale;
