/** @odoo-module **/

    // var ajax = require('web.ajax');
    import { WebClient } from "@web/webclient/webclient";
    import {patch} from "@web/core/utils/patch";
    // var { useBus, useService } = require("@web/core/utils/hooks");
    // var { useOwnDebugContext } = require("@web/core/debug/debug_context");
    // var { localization } = require("@web/core/l10n/localization");
    // var { Component, onMounted, useExternalListener, useState } = require("@odoo/owl");
    import { session } from '@web/session';


    patch(WebClient.prototype,{
        setup() {
            // this._super.apply(this, arguments);
            super.setup();
            var tab_title = session.sys_tab_name || 'iRoom';
            this.title.setParts({ zopenerp: tab_title }); // zopenerp is easy to grep
        }
    });
// });
