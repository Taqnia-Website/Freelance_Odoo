/** @odoo-module **/
import { registry } from "@web/core/registry";
// import { KpiCard } from "./kpi_card";
// import { ChartRender } from "./chart_render";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import { getColor } from "@web/core/colors/colors";
import { _t } from "@web/core/l10n/translation";

const { Component, onWillStart, useRef, onMounted, useState } = owl;
var selected_days = new Array();
var mousedown;
var selection = new Array();
var hotelname;
var froomname;
var croomname;
var mroomname;

export class CalenderDashboard extends Component {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.actionService = useService("action");
    this.start();
    this.shop_id = "";
    var from_date = "";
    var to_date = "";
    this.view_type = "month";
    this.date_detail = "";
    this.onMounted();
  }
  onMounted() {
    this.month_function();
  }

  async start() {
    var self = this;
    var shop = await this.orm.call("hotel.room_type", "list_shop", [0], {});
    $("#shops option[value='1']").remove();
    for (var i = 0; i < shop.length; i++) {
      $("#shops").append(
        $("<option>", {
          text: shop[i].name,
          value: shop[i].id,
        })
      );
    }
    this.total_detail();
  }
  async total_detail() {
    this.shop_id = $("#shops").val();
    var shop = this.shop_id;
    if (shop) {
      //console.log('shop_idkkkkkkkkkkk',shop)
      var detail = await this.orm.call("hotel.reservation", "get_datas", [0], {
        shop,
      });
      //console.log('sssssssssssssssssssssssssss',$('#check_in'))
      $("#check_in").html(detail.check_in);
      $("#check_out").html(detail.check_out);
      $("#total").html(detail.total);
      $("#booked").html(detail.booked);
    }
  }

  async reload() {
    this.total_detail();
    const dayNames = {
      Mon: "الإثنين",
      Tue: "الثلاثاء",
      Wed: "الأربعاء",
      Thu: "الخميس",
      Fri: "الجمعة",
      Sat: "السبت",
      Sun: "الأحد"
    };
    //console.log('haiiiiiiiiiiiiiiiiiiiiiiiiiii')
    //    $("#booking_calendar").html('<div class="fc-toolbar fc-header-toolbar"><div class="fc-left"><h2>Date</h2></div><div class="fc-right"><button type="button" class="fc-today-button fc-button fc-state-default fc-corner-left fc-corner-right fc-state-disabled" disabled="">Today</button><div class="fc-button-group"><button type="button" class="fc-prev-button fc-button fc-state-default fc-corner-left">&lt;</button><button type="button" class="fc-next-button fc-button fc-state-default">&gt;</button><button type="button" class="fc-month-button fc-button fc-state-default">Month</button><button type="button" class="fc-customWeek-button fc-button fc-state-default fc-corner-right fc-state-active" id="week_button" t-on-click="week_function">Week</button></div></div><div class="fc-center"></div><div class="fc-clear"></div></div>')
    $("#toolbar_box").css("display", "block");
    if ($("#tbl_dashboard").length == 0) {
      $("#booking_calendar").append(
        '<div class="booking_calendar_container"><div id="loading-spinner" class="spinner" style="display:none;"></div><table id="tbl_dashboard" class="CSSTableGenerator" ></table></div>'
      );
    }

    $("#tbl_dashboard").html("");
    var self = this;
    $("#date_detail").html(this.date_detail);
    self.next_date = new Date(self.from_date);
    var current_date = new Date();
    var current_date_format = `${current_date.getFullYear()}-${(
      current_date.getMonth() + 1
    )
      .toString()
      .padStart(2, "0")}-${current_date.getDate().toString().padStart(2, "0")}`;
    var th =
      '<th width="100px" height="27px" t-att-data-id="Room Type" class="fc-cell-room">نوع الغرفة</th>';
    var td;
    var tdmonths = '<td  width="200px" ><div class="extra_div"></div></td>';

    if (self.from_date > self.to_date) {
      alert("To Date must be greater than From Date");
      return true;
    }
    //*****************Creating Table headers**********************************
    var cnt = 0;
    while (self.next_date <= self.to_date) {
      var next_date_format = `${self.next_date.getFullYear()}-${(
        self.next_date.getMonth() + 1
      )
        .toString()
        .padStart(2, "0")}-${self.next_date
        .getDate()
        .toString()
        .padStart(2, "0")}`;
      var prev_date = new Date(self.next_date);
      prev_date.setDate(prev_date.getDate() - 1);
      if (next_date_format == current_date_format) {
        th =
          th +
          '<th style="background-color:#5ad4e4;">' +
          dayNames[self.next_date.toDateString().substr(0, 3)] +
          "<br/>" +
          self.next_date.getDate() +
          "</th>";
      } else {
        th =
          th +
          '<th class="fc-cell-content1">' +
          dayNames[self.next_date.toDateString().substr(0, 3)] +
          "<br/>" +
          self.next_date.getDate() +
          "</th>";
        tdmonths = tdmonths + "<td></td>";
      }

      self.next_date.setDate(self.next_date.getDate() + 1);
      cnt++;
    }

    $("#tbl_dashboard").append("<tr>" + th + "</tr>");
    // var claim_type = this.$el.find('#shops');
    var shop_id = $("#shops").val();
    if (shop_id) {
      self.next_date.setDate(self.next_date.getDate() - cnt);
      var roomtype = await this.orm.call(
        "hotel.room_type",
        "list_room_type",
        [0],
        { shop_id }
      );
      for (var i = 0; i < roomtype.length; i++) {
        var roomtypes =
          '<td class="fc-cell-rooms" clicked="false" t-att-data-id=' +
          roomtype[i].name +
          ">" +
          roomtype[i].name +
          "  " +
          '<span class="fa fa-sort-asc"></span></td>';
        $("#tbl_dashboard").append("<tr>" + roomtypes + "</tr>");

        var res = roomtype[i].id;
        var categ_id = roomtype[i].id;
        var room = await this.orm.call("hotel.room_type", "list_room", [0], {
          res,
          shop_id,
        });
        for (var j = 0; j < room.length; j++) {
          var tss = "";
          var room_id = room[j].id;
          var cater_id = roomtype[i].id;
          var shop_id = $("#shops").val();
          var hotelroom = await this.orm.call(
            "hotel.reservation",
            "search_reserve_room",
            [0],
            { room_id, cater_id, shop_id }
          );
          var dates = [];
          for (var h = 0; h < hotelroom.length; h++) {
            var checkin = hotelroom[h].checkin;
            var ref_no = hotelroom[h].ref_no;
            var boolean = hotelroom[h].boolean;
            checkin = checkin.split(" ")[0];
            // var chkinday = checkin[0].split('-')
            // chkinday = chkinday[chkinday.length-1]
            var status = hotelroom[h].status;
            var chkout = hotelroom[h].checkout;
            chkout = chkout.split(" ")[0];
            var id = hotelroom[h].id;
            // var chkoutday = chkout[0].split('-')
            // chkoutday = chkoutday[chkoutday.length-1]
            //console.log("cddddddddddddddddddddddddddddddddddddddddddddd",boolean,hotelroom[h].boolean)
            var days = {
              checkin: checkin,
              checkout: chkout,
              status: status,
              ref_no: ref_no,
              id: id,
              boolean: boolean,
            };
            dates.push(days);
          }
          self.next_date = new Date(self.from_date);
          var count = 0;
          if (room[j].name.indexOf(" ") !== -1) {
            hotelname = room[j].name.replace(/ /g, "-");
          } else {
            hotelname = room[j].name;
          }
          for (var s = 0; s <= cnt - 1; s++) {
            var month_id = (self.next_date.getMonth() + 1)
              .toString()
              .padStart(2, "0");
            tss =
              tss +
              '<td id="' +
              hotelname +
              "_" +
              self.next_date.getFullYear() +
              "-" +
              month_id +
              "-" +
              self.next_date.getDate().toString().padStart(2, "0") +
              '" class="fc-cell-content" data-id=' +
              room[j].id +
              " " +
              "room_type=" +
              roomtype[i].id +
              "></td>";
            self.next_date.setDate(self.next_date.getDate() + 1);
          }
          var roomtd =
            '<td class="fc-cell-roomname" room_type=' +
            roomtype[i].id +
            " t-att-data-id=" +
            room[j].name +
            ">" +
            room[j].name +
            tss +
            "</td>";
          $("#tbl_dashboard").append(
            "<tr class='" + roomtype[i].name + "'>" + roomtd + "</tr>"
          );
          for (var d = 0; d < dates.length; d++) {
            if (dates.length != 0) {
              if (
                dates[d]["status"] == "draft" &&
                dates[d]["boolean"] == true
              ) {
                var checkin_date = new Date(dates[d]["checkin"]);
                //console.log("55555555555555555555555555555555555",dates[d])
                var checkout_date = new Date(dates[d]["checkout"]);
                var ckn = $("#" + hotelname + "_" + dates[d]["checkin"]);
                ckn.text(dates[d]["ref_no"]);
                while (checkin_date <= checkout_date) {
                  var str_checkin_date = `${checkin_date.getFullYear()}-${(
                    checkin_date.getMonth() + 1
                  )
                    .toString()
                    .padStart(2, "0")}-${checkin_date
                    .getDate()
                    .toString()
                    .padStart(2, "0")}`;
                  var chin = $("#" + hotelname + "_" + str_checkin_date);

                  chin.removeClass("fc-cell-content");
                  chin.attr("class", "reserved");
                  chin.attr("data-id", dates[d]["id"]);
                  chin.css("background-color", "#9b59b6");
                  chin.css("disply", "flex");
                  chin.css("max-width", "40px");
                  chin.css("overflow", "unset");
                  checkin_date.setDate(checkin_date.getDate() + 1);
                }
              }

              if (
                dates[d]["status"] == "draft" &&
                dates[d]["boolean"] == false
              ) {
                var checkin_date = new Date(dates[d]["checkin"]);
                //console.log("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv",dates[d])
                var checkout_date = new Date(dates[d]["checkout"]);
                var ckn = $("#" + hotelname + "_" + dates[d]["checkin"]);
                ckn.text(dates[d]["ref_no"]);
                while (checkin_date <= checkout_date) {
                  var str_checkin_date = `${checkin_date.getFullYear()}-${(
                    checkin_date.getMonth() + 1
                  )
                    .toString()
                    .padStart(2, "0")}-${checkin_date
                    .getDate()
                    .toString()
                    .padStart(2, "0")}`;
                  var chin = $("#" + hotelname + "_" + str_checkin_date);

                  chin.removeClass("fc-cell-content");
                  chin.attr("class", "reserved");
                  chin.attr("data-id", dates[d]["id"]);
                  chin.css("background-color", "#bfe1f4");
                  chin.css("disply", "flex");
                  chin.css("max-width", "40px");
                  chin.css("overflow", "unset");
                  checkin_date.setDate(checkin_date.getDate() + 1);
                }
              }

              //console.log("666666666666666666666666666vvvvvvvv",dates[d]['boolean'])

              if (
                dates[d]["status"] == "confirm" &&
                dates[d]["boolean"] == true
              ) {
                //console.log("666666666666666666666666666")
                var checkin_date = new Date(dates[d]["checkin"]);
                var checkout_date = new Date(dates[d]["checkout"]);
                var ckn = $("#" + hotelname + "_" + dates[d]["checkin"]);
                ckn.text(dates[d]["ref_no"]);
                while (checkin_date <= checkout_date) {
                  var str_checkin_date = `${checkin_date.getFullYear()}-${(
                    checkin_date.getMonth() + 1
                  )
                    .toString()
                    .padStart(2, "0")}-${checkin_date
                    .getDate()
                    .toString()
                    .padStart(2, "0")}`;
                  var chin = $("#" + hotelname + "_" + str_checkin_date);
                  chin.attr("data-id", dates[d]["id"]);
                  chin.removeClass("fc-cell-content");
                  chin.attr("class", "reserved");
                  chin.css("background-color", "#9b59b6");
                  chin.css("disply", "flex");
                  chin.css("max-width", "40px");
                  chin.css("overflow", "unset");
                  checkin_date.setDate(checkin_date.getDate() + 1);
                }
              }
              if (
                dates[d]["status"] == "confirm" &&
                dates[d]["boolean"] == false
              ) {
                //console.log("vvvvvvvvvvvvvvvvvvvvvvvvvxxxxxx11111")
                var checkin_date = new Date(dates[d]["checkin"]);
                var checkout_date = new Date(dates[d]["checkout"]);
                var ckn = $("#" + hotelname + "_" + dates[d]["checkin"]);
                ckn.text(dates[d]["ref_no"]);
                while (checkin_date <= checkout_date) {
                  var str_checkin_date = `${checkin_date.getFullYear()}-${(
                    checkin_date.getMonth() + 1
                  )
                    .toString()
                    .padStart(2, "0")}-${checkin_date
                    .getDate()
                    .toString()
                    .padStart(2, "0")}`;
                  var chin = $("#" + hotelname + "_" + str_checkin_date);
                  chin.attr("data-id", dates[d]["id"]);
                  chin.removeClass("fc-cell-content");
                  chin.attr("class", "reserved");
                  chin.css("background-color", "#e6d0bb");
                  chin.css("disply", "flex");
                  chin.css("max-width", "40px");
                  chin.css("overflow", "unset");
                  checkin_date.setDate(checkin_date.getDate() + 1);
                }
              }
            }
          }
        }
      }

      var shop_id = $("#shops").val();
      var folio_detail = await this.orm.call(
        "hotel.reservation",
        "search_folio",
        [0],
        { shop_id }
      );
      for (var f = 0; f < folio_detail.length; f++) {
        var checkin = folio_detail[f].checkin;
        checkin = checkin.split(" ")[0];
        var status = folio_detail[f].status;
        var chkout = folio_detail[f].checkout;
        chkout = chkout.split(" ")[0];
        if (folio_detail[f].room_name.indexOf(" ") !== -1) {
          froomname = folio_detail[f].room_name.replace(/ /g, "-");
        } else {
          froomname = folio_detail[f].room_name;
        }
        if (status != "check_out" && status != "done" && status != "cancel") {
          var checkin_date = new Date(checkin);
          var checkout_date = new Date(chkout);
          var ckn = $("#" + froomname + "_" + checkin);
          ckn.text(folio_detail[f].fol_no);
          while (checkin_date <= checkout_date) {
            var str_checkin_date = `${checkin_date.getFullYear()}-${(
              checkin_date.getMonth() + 1
            )
              .toString()
              .padStart(2, "0")}-${checkin_date
              .getDate()
              .toString()
              .padStart(2, "0")}`;
            var chin = $("#" + froomname + "_" + str_checkin_date);
            chin.removeClass("fc-cell-content");
            chin.attr("class", "folio");
            chin.attr("data-id", folio_detail[f].id);
            chin.css("background-color", "#b5dcd1");
            chin.css("disply", "flex");
            chin.css("max-width", "40px");
            chin.css("overflow", "unset");
            checkin_date.setDate(checkin_date.getDate() + 1);
          }
        }
        if (status == "check_out" || status == "done") {
          var checkin_date = new Date(checkin);
          var checkout_date = new Date(chkout);
          var ckn = $("#" + froomname + "_" + checkin);
          ckn.text(folio_detail[f].fol_no);
          while (checkin_date <= checkout_date) {
            var str_checkin_date = `${checkin_date.getFullYear()}-${(
              checkin_date.getMonth() + 1
            )
              .toString()
              .padStart(2, "0")}-${checkin_date
              .getDate()
              .toString()
              .padStart(2, "0")}`;
            var chin = $("#" + froomname + "_" + str_checkin_date);
            chin.removeClass("fc-cell-content");
            chin.attr("class", "folio");
            chin.attr("data-id", folio_detail[f].id);
            chin.css("background-color", "#fcd0bb");
            chin.css("disply", "flex");
            chin.css("max-width", "40px");
            chin.css("overflow", "unset");
            checkin_date.setDate(checkin_date.getDate() + 1);
          }
        }
      }
      var shop_id = $("#shops").val();
      var cleaning_detail = await this.orm.call(
        "hotel.reservation",
        "search_cleaning",
        [0],
        { shop_id }
      );
      for (var g = 0; g < cleaning_detail.length; g++) {
        var checkin = cleaning_detail[g].checkin;
        checkin = checkin.split(" ")[0];
        var status = cleaning_detail[g].status;
        var chkout = cleaning_detail[g].checkout;
        chkout = chkout.split(" ")[0];
        if (cleaning_detail[g].room_no.indexOf(" ") !== -1) {
          croomname = cleaning_detail[g].room_no.replace(/ /g, "-");
        } else {
          croomname = cleaning_detail[g].room_no;
        }
        if (status != "done") {
          var checkin_date = new Date(checkin);
          var checkout_date = new Date(chkout);
          var ckn = $("#" + croomname + "_" + checkin);
          ckn.text("Unavilable");
          while (checkin_date <= checkout_date) {
            var str_checkin_date = `${checkin_date.getFullYear()}-${(
              checkin_date.getMonth() + 1
            )
              .toString()
              .padStart(2, "0")}-${checkin_date
              .getDate()
              .toString()
              .padStart(2, "0")}`;
            var chin = $("#" + croomname + "_" + str_checkin_date);
            chin.removeClass("fc-cell-content");
            chin.attr("class", "cleaning");
            chin.css("overflow", "hidden");
            chin.css("background-color", "#dfe4e4");
            chin.attr("data-id", cleaning_detail[g].id);
            checkin_date.setDate(checkin_date.getDate() + 1);
          }
        }
      }
      var shop_id = $("#shops").val();
      var repair_detail = await this.orm.call(
        "hotel.reservation",
        "search_repair",
        [0],
        { shop_id }
      );
      for (var l = 0; l < repair_detail.length; l++) {
        var date = repair_detail[l].date;
        dates = date.split(" ")[0];
        var status = repair_detail[l].status;
        if (repair_detail[l].room_no.indexOf(" ") !== -1) {
          mroomname = repair_detail[l].room_no.replace(/ /g, "-");
        } else {
          mroomname = repair_detail[l].room_no;
        }
        // var chkout = repair_detail[l].checkout
        var date2 = dates;
        if (status != "done") {
          var checkin_date = new Date(dates);
          var checkout_date = new Date(date2);
          var ckn = $("#" + mroomname + "_" + dates);
          ckn.text("Maintenance");
          while (checkin_date <= checkout_date) {
            var str_checkin_date = `${checkin_date.getFullYear()}-${(
              checkin_date.getMonth() + 1
            )
              .toString()
              .padStart(2, "0")}-${checkin_date
              .getDate()
              .toString()
              .padStart(2, "0")}`;
            var chin = $("#" + mroomname + "_" + str_checkin_date);
            chin.removeClass("fc-cell-content");
            chin.attr("class", "repair");
            chin.css("background-color", "#dbc3e4");
            chin.css("overflow", "hidden");
            chin.css("max-width", "40px");
            chin.attr("data-id", repair_detail[l].id);
            checkin_date.setDate(checkin_date.getDate() + 1);
          }
        }
      }
    }

    function pad(number) {
      if (number < 10) {
        return "0" + number;
      }
      return number;
    }

    $(".fc-cell-content").mouseup(async function (ev) {
      ev.preventDefault();
      mousedown = false;
      for (var m = 0; m < selection.length; m++) {
        $("#" + selection[m]).css("backgroundColor", "");
        $("#" + selection[m]).css("outline", "none");
      }
      var checkout = this.id.split("_")[1];
      var room = $("#" + this.id).attr("data-id");
      var room_type = $("#" + this.id).attr("room_type");
      selected_days.push(checkout);
      var checkin = selected_days[0];
      var details = await self.orm.call(
        "hotel.reservation",
        "create_detail",
        [0],
        { room, room_type, checkout, checkin }
      );
      var shop_id = $("#shops").val();
      var startdate = new Date(selected_days[0]);
      var enddate = new Date(selected_days[1]);
      var currentdate = new Date();
      const yesterday = new Date(currentdate.getTime() - 1000 * 60 * 60 * 24);
      if (startdate > enddate) {
        window.alert("Checkin Date must be less than Checkout Date");
      } else if (yesterday >= startdate) {
        window.alert("Checkin Date must be Equal or Greater than today");
      } else {
        self.actionService.doAction({
          name: _t("Hotel Reservation"),
          res_model: "hotel.reservation",
          views: [[false, "form"]],
          view_mode: "form",
          type: "ir.actions.act_window",
          target: "new",
          context: {
            default_shop_id: Number(shop_id),
            default_reservation_line: [
              {
                checkin: checkin,
                checkout: details[0].checkout,
                categ_id: parseInt(details[0].cat_id),
                room_number: parseInt(details[0].room),
                price: parseInt(details[0].price),
                company_id: parseInt(shop_id),
              },
            ],
          },
        });
      }
    });
    $(".reserved").mousedown(async function (ev) {
      ev.preventDefault();
      var view_id = await self.orm.call(
        "hotel.reservation",
        "get_view_reserve",
        [0],
        {}
      );
      //console.log('--------------------------',view_id);
      var checkin = this.id.split("_")[1];
      var id = $("#" + this.id).attr("data-id");
      if (id) {
        self.actionService.doAction({
          name: _t("Hotel Reservation"),
          res_model: "hotel.reservation",
          res_id: parseInt(id),
          views: [[view_id, "form"]],
          view_mode: "form",
          type: "ir.actions.act_window",
          target: "new",
          context: {},
        });
      }
    });
    // $('.folio').mousedown(async function(ev) {
    // 	ev.preventDefault();
    // 	var checkin = this.id.split('_')[1]
    // 	var id = $('#' + this.id).attr('data-id');
    // 	var agent = await self.orm.call('hotel.reservation', 'check_user', [0], {})
    // 	if(agent == false){
    // 		alert(_t("User access rights, kindly ask your admin to provide you access right to see details."));
    // 	}else{
    // 		self.actionService.doAction({
    // 			name : _t("Folio"),
    // 			res_model : 'hotel.folio',
    // 			res_id : parseInt(id),
    // 			views : [[false, 'form']],
    // 			view_mode : 'form',
    // 			type : 'ir.actions.act_window',
    // 			target : "new",
    // 			context : {
    // 			},

    // 	})
    // }

    // })
    $(".folio").mousedown(async function (ev) {
      ev.preventDefault();
      var checkin = this.id.split("_")[1];
      var id = $("#" + this.id).attr("data-id");

      self.actionService.doAction({
        name: _t("Folio"),
        res_model: "hotel.folio",
        res_id: parseInt(id),
        views: [[false, "form"]],
        view_mode: "form",
        type: "ir.actions.act_window",
        target: "new",
        context: {},
      });
    });

    // $('.cleaning').mousedown(async function(ev) {
    // 	ev.preventDefault();
    // 	var checkin = this.id.split('_')[1]
    // 	var id = $('#' + this.id).attr('data-id');
    // 	var agent = await self.orm.call('hotel.reservation', 'check_user', [0], {})
    // 	if(agent == false){
    // 		alert(_t("User access rights, kindly ask your admin to provide you access right to see details."));
    // 	}else{

    // 		self.actionService.doAction({
    // 			name : _t("Housekeeping"),
    // 			res_model : 'hotel.housekeeping',
    // 			res_id : parseInt(id),
    // 			views : [[false, 'form']],
    // 			view_mode : 'form',
    // 			type : 'ir.actions.act_window',
    // 			target : "new",
    // 			context : {
    // 			},

    // 	})
    // }

    // })
    $(".cleaning").mousedown(async function (ev) {
      ev.preventDefault();
      var checkin = this.id.split("_")[1];
      var id = $("#" + this.id).attr("data-id");
      self.actionService.doAction({
        name: _t("Housekeeping"),
        res_model: "hotel.housekeeping",
        res_id: parseInt(id),
        views: [[false, "form"]],
        view_mode: "form",
        type: "ir.actions.act_window",
        target: "new",
        context: {},
      });
    });

    // $('.repair').mousedown(async function(ev) {
    // 	ev.preventDefault();
    // 	var date = this.id.split('_')[1]
    // 	var id = $('#' + this.id).attr('data-id');
    // 	var agent = await self.orm.call('hotel.reservation', 'check_user', [0], {})
    // 	if(agent == false){
    // 		alert(_t("User access rights, kindly ask your admin to provide you access right to see details."));
    // 	}else{

    // 		self.actionService.doAction({
    // 			name : _t("Request for Repair / Replacement"),
    // 			res_model : 'rr.housekeeping',
    // 			res_id : parseInt(id),
    // 			views : [[false, 'form']],
    // 			view_mode : 'form',
    // 			type : 'ir.actions.act_window',
    // 			target : "new",
    // 			context : {
    // 			},

    // 	})
    // }

    // })
    $(".repair").mousedown(async function (ev) {
      ev.preventDefault();
      var date = this.id.split("_")[1];
      var id = $("#" + this.id).attr("data-id");
      var agent = await self.orm.call(
        "hotel.reservation",
        "check_user",
        [0],
        {}
      );

      self.actionService.doAction({
        name: _t("Request for Repair / Replacement"),
        res_model: "rr.housekeeping",
        res_id: parseInt(id),
        views: [[false, "form"]],
        view_mode: "form",
        type: "ir.actions.act_window",
        target: "new",
        context: {},
      });
    });
    $(".fc-cell-content").mousedown(function (ev) {
      mousedown = true;
      selection.length = 0;
      selected_days.length = 0;
      ev.preventDefault();
      var checkin = this.id.split("_")[1];
      selected_days.push(checkin);
      selection.push(this.id);
    });
    $(".fc-cell-content").mouseover(function () {
      if (mousedown) {
        $("#" + selection[0]).attr("style", "background-color: #eee;");
        $("#" + selection[0]).css("outline", "1px solid #ccc");
        this.style.backgroundColor = "#eee";
        this.style.outline = "1px solid #ccc";
        selection.push(this.id);
      }
    });
    $(".reserved").mouseover(async function () {
      //console.log('workingppppppppppppppppppppppppp', this)
      // var tooltipText = $(this).data('tooltip');
      console.log("sssssssssssssssssssssssssssss");
      var id = $("#" + this.id).attr("data-id");
      var reserve = await self.orm.call(
        "hotel.reservation",
        "reserve_room",
        [0],
        { id }
      );
      if (reserve.length > 0) {
        $("#" + this.id).attr("data-toggle", "tooltip");
        $("#" + this.id).attr("data-placement", "top");
        $("#" + this.id).attr(
          "title",
          "Reservation No: " +
            reserve[0].res_no +
            "\n" +
            "Customer: " +
            reserve[0].partner +
            "\n" +
            "Checkin: " +
            reserve[0].checkin +
            "\n" +
            "Checkout: " +
            reserve[0].checkout +
            "\n" +
            "Status: " +
            reserve[0].state
        );
      }
    });

    $(".folio").mouseover(async function () {
      //console.log('workingppppppppppppppppppppppppp', this)
      // var tooltipText = $(this).data('tooltip');
      //console.log('sssssssssssssssssssssssssssss',)
      var id = $("#" + this.id).attr("data-id");
      var folio = await self.orm.call(
        "hotel.reservation",
        "folio_detail",
        [0],
        { id }
      );
      if (folio.length > 0) {
        $("#" + this.id).attr("data-toggle", "tooltip");
        $("#" + this.id).attr("data-placement", "top");
        $("#" + this.id).attr(
          "title",
          "Reservation No: " +
            folio[0].res_no +
            "\n" +
            "Customer: " +
            folio[0].partner +
            "\n" +
            "Checkin: " +
            folio[0].checkin +
            "\n" +
            "Checkout: " +
            folio[0].checkout +
            "\n" +
            "Status: " +
            folio[0].state
        );
      }
    });
    $(".cleaning").mouseover(async function () {
      //console.log('workingppppppppppppppppppppppppp', this)
      // var tooltipText = $(this).data('tooltip');
      console.log("sssssssssssssssssssssssssssss");
      var id = $("#" + this.id).attr("data-id");
      var clean = await self.orm.call(
        "hotel.reservation",
        "cleaning_detail",
        [0],
        { id }
      );
      if (clean.length > 0) {
        $("#" + this.id).attr("data-toggle", "tooltip");
        $("#" + this.id).attr("data-placement", "top");
        $("#" + this.id).attr(
          "title",
          "Name: " +
            clean[0].name +
            "\n" +
            "Start date: " +
            clean[0].start +
            "\n" +
            "End date: " +
            clean[0].end +
            "\n" +
            "Inspector: " +
            clean[0].inspector +
            "\n" +
            "Status: " +
            clean[0].state
        );
      }
    });
    $(".repair").mouseover(async function () {
      //console.log('workingppppppppppppppppppppppppp', this)
      //console.log('sssssssssssssssssssssssssssss',)
      var id = $("#" + this.id).attr("data-id");
      var replace = await self.orm.call(
        "hotel.reservation",
        "repair_repace_detail",
        [0],
        { id }
      );
      if (replace.length > 0) {
        $("#" + this.id).attr("data-toggle", "tooltip");
        $("#" + this.id).attr("data-placement", "top");
        $("#" + this.id).attr(
          "title",
          "Name: " +
            replace[0].name +
            "\n" +
            "ordered date: " +
            replace[0].date +
            "\n" +
            "Activity: " +
            replace[0].activity +
            "\n" +
            "Requested By: " +
            replace[0].request +
            "\n" +
            "Approved By: " +
            replace[0].approved +
            "\n" +
            "Status: " +
            replace[0].state
        );
      }
    });

    $(document).ready(function () {
      // Select all elements with class 'fc-cell-rooms'
      var $records = $(".fc-cell-rooms");

      // Hide all elements except the first one
      //  $records.each(function(index) {
      //    if (index !== 0) { // hide all except the first one
      //        var type = $(this).attr('t-att-data-id');
      //        $('.' + type).css('display', 'none');
      //        $(this).attr('clicked', 'false');
      //     } else { // show the first one
      //        var type = $(this).attr('t-att-data-id');
      //        $('.' + type).removeAttr('style');
      //        $(this).attr('clicked', 'true');
      //    }
      //  });

      // Handle click event
      $(".fc-cell-rooms").click(function () {
        var type = $(this).attr("t-att-data-id");
        var clicked = $(this).attr("clicked");

        if (clicked === "false") {
          // Hide other records and show the clicked one
          $("." + type).css("display", "none");
          $(this).children().removeClass().addClass("fa fa-sort-desc");
          $(this).attr("clicked", "true");
        } else {
          // Show the records corresponding to the clicked one
          $("." + type).removeAttr("style");
          $(this).children().removeClass().addClass("fa fa-sort-asc");
          $(this).attr("clicked", "false");
        }
      });
    });

    var $container = $(".booking_calendar_container");
    var $table = $("#tbl_dashboard");
    var rowCount = $table.find("tr").length;

    if (rowCount > 1 && rowCount <= 6) {
      $container.css("height", "auto");
      $(".fc-cell-room").addClass("tbl-vertical-row" + rowCount);
    } else if (rowCount <= 1) {
      $container.css("height", "auto");
      $(".fc-cell-room").addClass("tbl-vertical-row0");
    } else if (rowCount > 6) {
      $container.css("height", "60vh");
      $(".fc-cell-room").addClass("tbl-vertical-row7");
    }
  }

  async week_function() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const day = today.getDay();
    const daysToSubtract = day === 0 ? 6 : day - 1;
    const startDate = new Date(
      today.getTime() - daysToSubtract * 24 * 60 * 60 * 1000
    );
    const endDate = new Date(startDate.getTime() + 6 * 24 * 60 * 60 * 1000);
    const monthNames = [
  "يناير",  // January
  "فبراير", // February
  "مارس",    // March
  "أبريل",  // April
  "مايو",   // May
  "يونيو",  // June
  "يوليو",  // July
  "أغسطس",  // August
  "سبتمبر", // September
  "أكتوبر", // October
  "نوفمبر", // November
  "ديسمبر"  // December
    ];

    const days = startDate.getDate();
    const month = monthNames[startDate.getMonth()];
    const year = startDate.getFullYear();
    const endday = endDate.getDate();
    const endmonth = monthNames[endDate.getMonth()];
    const endyear = endDate.getFullYear();
    this.date_detail = `${days} ${month} ${year} - ${endday} ${endmonth} ${endyear}`;
    this.from_date = startDate;
    this.to_date = endDate;
    this.view_type = "week";
    this.reload();
  }

  async month_function() {
    const today = new Date();
    today.setDate(1);
    today.setHours(0, 0, 0, 0);
    const month = today.getMonth();
    const endDate = new Date(today.getFullYear(), month + 1, 0);
    const year = today.getFullYear();
    const startDate = `${year}-${month + 1}-01`;
    const monthNames = [
        "يناير",  // January
        "فبراير", // February
        "مارس",    // March
        "أبريل",  // April
        "مايو",   // May
        "يونيو",  // June
        "يوليو",  // July
        "أغسطس",  // August
        "سبتمبر", // September
        "أكتوبر", // October
        "نوفمبر", // November
        "ديسمبر"  // December
    ];
    this.date_detail = monthNames[month];
    // $('#date_detail').val(nextMonthName)
    // console.log('0000000000000000000000000000000',$('#date_detail').val())
    this.from_date = startDate;
    this.to_date = endDate;
    this.view_type = "month";
    this.reload();
  }

  async preview_function() {
    if (this.view_type == "week") {
      const startDate = new Date(this.from_date);
      const endDate = new Date(this.to_date);
      const daysToSubtract = 7;
      const previousStartDate = new Date(
        startDate.getTime() - daysToSubtract * 24 * 60 * 60 * 1000
      );
      const previousEndDate = new Date(
        endDate.getTime() - daysToSubtract * 24 * 60 * 60 * 1000
      );
      const monthNames = [
  "يناير",  // January
  "فبراير", // February
  "مارس",    // March
  "أبريل",  // April
  "مايو",   // May
  "يونيو",  // June
  "يوليو",  // July
  "أغسطس",  // August
  "سبتمبر", // September
  "أكتوبر", // October
  "نوفمبر", // November
  "ديسمبر"  // December
      ];

      const day = previousStartDate.getDate();
      const month = monthNames[previousStartDate.getMonth()];
      const year = previousStartDate.getFullYear();
      const endday = previousEndDate.getDate();
      const endmonth = monthNames[previousEndDate.getMonth()];
      const endyear = previousEndDate.getFullYear();
      this.date_detail = `${day} ${month} ${year} - ${endday} ${endmonth} ${endyear}`;
      this.from_date = previousStartDate;
      this.to_date = previousEndDate;
      this.reload();
    } else {
      const startDate = new Date(this.from_date);
      const endDate = new Date(this.to_date);
      const month = startDate.getMonth();
      const year = startDate.getFullYear();
      const previousMonth = new Date(year, month - 1, 1);
      const previousMonthEndDate = new Date(
        endDate.getFullYear(),
        endDate.getMonth(),
        0
      );
      const monthNames = [
        "يناير",  // January
        "فبراير", // February
        "مارس",    // March
        "أبريل",  // April
        "مايو",   // May
        "يونيو",  // June
        "يوليو",  // July
        "أغسطس",  // August
        "سبتمبر", // September
        "أكتوبر", // October
        "نوفمبر", // November
        "ديسمبر"  // December
      ];
      this.date_detail = monthNames[previousMonth.getMonth()];
      // $('#date_detail').val(nextMonthName)
      this.from_date = previousMonth;
      this.to_date = previousMonthEndDate;
      this.reload();
    }
  }

  async next_function() {
    if (this.view_type == "week") {
      const startDate = new Date(this.from_date);
      const endDate = new Date(this.to_date);
      const daysToSubtract = 7;
      const nextStartDate = new Date(
        startDate.getTime() + daysToSubtract * 24 * 60 * 60 * 1000
      );
      const nextEndDate = new Date(
        endDate.getTime() + daysToSubtract * 24 * 60 * 60 * 1000
      );
      const monthNames = [
  "يناير",  // January
  "فبراير", // February
  "مارس",    // March
  "أبريل",  // April
  "مايو",   // May
  "يونيو",  // June
  "يوليو",  // July
  "أغسطس",  // August
  "سبتمبر", // September
  "أكتوبر", // October
  "نوفمبر", // November
  "ديسمبر"  // December
      ];

      const days = nextStartDate.getDate();
      const month = monthNames[nextStartDate.getMonth()];
      const year = nextStartDate.getFullYear();
      const endday = nextEndDate.getDate();
      const endmonth = monthNames[nextEndDate.getMonth()];
      const endyear = nextEndDate.getFullYear();
      this.date_detail = `${days} ${month} ${year} - ${endday} ${endmonth} ${endyear}`;
      this.from_date = nextStartDate;
      this.to_date = nextEndDate;
      this.reload();
    } else {
      const startDate = new Date(this.from_date);
      const endDate = new Date(this.to_date);
      const month = startDate.getMonth();
      const year = startDate.getFullYear();
      const nextMonth = new Date(year, month + 1, 1);
      const nextMonthLastDay = new Date(
        nextMonth.getFullYear(),
        nextMonth.getMonth() + 1,
        0
      );
      const monthNames = [
        "يناير",  // January
        "فبراير", // February
        "مارس",    // March
        "أبريل",  // April
        "مايو",   // May
        "يونيو",  // June
        "يوليو",  // July
        "أغسطس",  // August
        "سبتمبر", // September
        "أكتوبر", // October
        "نوفمبر", // November
        "ديسمبر"  // December
      ];
      const nextMonthName = monthNames[nextMonth.getMonth()];
      this.date_detail = nextMonthName;
      this.from_date = nextMonth;
      this.to_date = nextMonthLastDay;
      this.reload();
    }
  }
  async today_function() {
    if (this.view_type == "week") {
      this.week_function();
    } else {
      this.month_function();
    }
  }
}

CalenderDashboard.template = "hotel_dashboard_template";
registry.category("actions").add("HotelDashboardView_temp", CalenderDashboard);
