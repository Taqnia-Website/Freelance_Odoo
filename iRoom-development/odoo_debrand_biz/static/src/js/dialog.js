/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
patch(Dialog.prototype, {
    setup() {
        // this._super.apply(this, arguments);
        super.setup();
        const odoo_replacement_text = session.odoo_replacement_text || "iRoom";
        this.title = odoo_replacement_text;
        this.props.title = odoo_replacement_text;
    },
});