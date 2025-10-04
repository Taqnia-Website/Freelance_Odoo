/** @odoo-module **/
import {
    ClientErrorDialog, ErrorDialog, NetworkErrorDialog, RPCErrorDialog, SessionExpiredDialog }
     from "@web/core/errors/error_dialogs";
import { _lt } from "@web/core/l10n/translation";

ClientErrorDialog.title = _lt("iRoom Client Error");
NetworkErrorDialog.title = _lt("iRoom Network Error");
SessionExpiredDialog.title = _lt("iRoom Session Expired");
ErrorDialog.title = _lt("iRoom Error");
RPCErrorDialog.title = _lt("iRoom Error");