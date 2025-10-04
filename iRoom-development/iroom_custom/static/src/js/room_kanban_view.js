/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
//import { PurchaseDashBoard } from '@purchase/views/purchase_dashboard';


export class RoomDashBoardKanbanRenderer extends KanbanRenderer {};

RoomDashBoardKanbanRenderer.template = 'iroom_custom.RoomKanbanView';
RoomDashBoardKanbanRenderer.components= Object.assign({}, KanbanRenderer.components)

export const RoomDashBoardKanbanView = {
    ...kanbanView,
    Renderer: RoomDashBoardKanbanRenderer,
};

registry.category("views").add("room_legend_kanban", RoomDashBoardKanbanView);
