/** @odoo-module **/

import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { registry } from "@web/core/registry";
import { useService, onMounted } from "@web/core/utils/hooks";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { _t } from "@web/core/l10n/translation";
import { ListView } from "@web/views/list/list_view";

import { deserializeDate } from "@web/core/l10n/dates";

const { Component, useState } = owl;

var $primary = '#7367F0';
var $danger = '#EA5455';
var $warning = '#FF9F43';
var $info = '#00cfe8';
var $success = '#00db89';
var $primary_light = '#9c8cfc';
var $warning_light = '#FFC085';
var $danger_light = '#f29292';
var $info_light = '#1edec5';
var $label_color = '#e7eef7';
var $purple = '#df87f2';
var $white = '#fff';

var colors = [$primary, $danger, $warning, $info, $success, $purple, $white];
var light_colors = [$primary_light, $warning_light, $danger_light, $info_light, $success, $purple, $white];
var themeColors = ['#18458b', '#28C76F', '#EA5455', '#FF9F43', '#00cfe8'];

export class HotelReservationViewDashboard extends Component {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.nameService = useService("name");
        this.companyService = useService("company");

        // Initializing state variables
        var today = new Date();
        var todayObj = deserializeDate(`${today.getFullYear()}-${(today.getMonth()+1).toString().padStart(2, '0')}-${today.getDate().toString().padStart(2, '0')}`);
        this.state = useState({
            hotelFilter: [],
            reservation: [],
            selectedHotel: null,
            dateFrom: todayObj,
            dateTo: todayObj,
            hotel_id: null,
            doughnutChart: null,
            myBarChartVia: null,
            doughnutChartSource: null,
            doughnutChartHouseKeep: null,
            doughnutChartOccupiedRoom: null,
            occupancyBarChart: null,
            genderChart: null,
            countryChart: null,
            countryData: [],
            adultsChildrenChart: null,
            filter_data: {},
            roomAvailabilityData: [],
            servicesData: {},
            occupancyTableData: {},
            ratingTableData: {},
            loading: true,
            serviceLoading: true,
            occupyLoading: true,
            ratingLoading: true,
            DashboardModel: "ab.hotel.dashboard",

        });
        this.start();
        // DOM mounted hook
//        onMounted(() => {
//            this.start();
//        });
    }

    static components = { DateTimeInput, MultiRecordSelector,ListView };
    fromPlaceholder = _t("Date from...");
    toPlaceholder = _t("Date to...");

    // Fetch data and initialize charts
    async start() {
        await this.reservation_dashboard();
    }

    get filter() {
        return { label: _t("Hotel"), modelName: "sale.shop", id: [] };
    }

    get getDomain() {
        return [['company_id', 'in', Object.values(this.companyService.activeCompanyIds)]];
    }

    get filterValue() {
        return this.filter.id;
    }

    translate(text) {
        return _t(text);
    }

    get getDateFrom(){
        return this.state.dateFrom;
    }
    get getDateTo(){
        return this.state.dateTo;
    }
    // Main function to load dashboard data
    async reservation_dashboard() {

        this.state.filter_data.hotel_ids = this.state.hotel_id;
        this.state.filter_data.dateFrom = this.state.dateFrom;
        this.state.filter_data.dateTo = this.state.dateTo;
        let filter_data = this.state.filter_data;
        var DashboardModel = this.state.DashboardModel;
        const countryTotals = await this.orm.call(DashboardModel, "get_total_adults_and_children_per_country", [], filter_data);
        const reservationDataSource = await this.orm.call(DashboardModel, "count_reservations_by_source", [], filter_data);
        const reservationData = await this.orm.call(DashboardModel, "count_reservations_by_status", [], filter_data);
        const reservationDataVia = await this.orm.call(DashboardModel, "count_reservations_by_via", [], filter_data);
        const genderCounts = await this.orm.call(DashboardModel, "get_gender_counts", [], filter_data);
        const countryCounts = await this.orm.call(DashboardModel, "get_country_counts", [], filter_data);
        const currentBookings = await this.orm.call(DashboardModel, "get_current_bookings", [], filter_data);
        const houseKeepings = await this.orm.call(DashboardModel, "get_house_keepings", [], filter_data);
        const occupiedRooms = await this.orm.call(DashboardModel, "get_occupied_rooms", [], filter_data);
        const occupancyData = await this.orm.call(DashboardModel, "get_occupancy", [], filter_data);

        // Render room availability doughnut chart
        this.state.countryData = countryTotals;

//        this.renderDoughnutChart(Object.keys(reservationData), Object.values(reservationData));
        this.renderReservationBar(reservationData);
        this.rendeChartVia(reservationDataVia);
        this.renderOccuppancyBarChart(occupancyData);

        // Pie Charts
        this.renderDoughnutChartSource(Object.entries(reservationDataSource));
        this.renderDoughnutChartHouseKeep(Object.entries(houseKeepings));
        this.renderDoughnutChartOccupied(Object.entries(occupiedRooms));

        this.displayCounts(genderCounts, countryCounts);
        this.displayCurrentBookings(currentBookings);
        this.renderCountryBarChart(countryTotals);
        this.loadRoomAvailabilityData();
        this.loadServicesData();
        this.loadOccupyTableData();
        this.loadRatingTableData();
//        this.renderRoomAvailabilityChart(roomData);
    }

    // Handle date selection changes
    async onDateFromChanged(dateFrom) {
        this.state.dateFrom = dateFrom;
        await this.reservation_dashboard();
    }

    async onTagSelected(id, resIds) {
        this.state.hotel_id = resIds;
        await this.reservation_dashboard();
    }

    async onDateToChanged(dateTo) {
        this.state.dateTo = dateTo;
        await this.reservation_dashboard();
    }

    renderReservationBar(reservationData) {
        const $ctx = $("#reservationsChart");
            if (!$ctx) {
                console.error("Doughnut chart canvas not found");
                return;
            }
	    $ctx.empty();
        const count_total_bookings = Object.values(reservationData).reduce((total, value) => total + value, 0);

        Object.entries(reservationData).forEach(([state, count], index) => {
            var progressbar = this.renderBar(state, count, count_total_bookings, index);
            $ctx.append(progressbar)
        });
    }

    renderBar(label, count, count_total, index) {
        if (count_total){
            var color = index % 5;
            var percent = Math.round(count*100/count_total)
            return `
                <div class="label row mb-1 text-capitalize">
                    <span class="d-inline-block col text-start"><em>${label}</em></span>
                    <span class="d-inline-block col text-end"><em>${count}</em></span>
                </div>
                <div class="progress mb-3">
                    <div class="progress-bar pr-${color}" role="progressbar" style="width: ${percent}%;" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100">
                        ${percent}%
                    </div>
                </div>

        `}
        return '';
    }


    // Render Doughnut Chart for Reservation Status
    renderDoughnutChart(labels, data) { // TODO: Not used now
        const ctx = document.getElementById("myDoughnutChart");
        if (!ctx) {
            console.error("Doughnut chart canvas not found");
            return;
        }

        if (!labels || !data || labels.length === 0 || data.length === 0) {
            console.error("No data available for the chart");
            return;
        }

        const chartData = {
            labels: labels,
            datasets: [{
                label: "Reservation Status",
                data: data,
                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                hoverOffset: 4
            }]
        };

        const config = {
            type: "doughnut",
            data: chartData,
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "top" },
                    title: { display: true, text: "Reservation Status Doughnut Chart" }
                }
            }
        };

        if (this.state.doughnutChart) {
            this.state.doughnutChart.destroy();
        }

        this.state.doughnutChart = new Chart(ctx, config);
    }
    // Render Bar Chart for Reservation Status
    rendeChartVia(reservationDataVia) {
        const viaData = Object.entries(reservationDataVia).map(([key, value]) => ({ via: key, count: value }));
        this.renderBarChart("myBarChartVia", viaData, "Reservation Type", "via", "count");

    }

    // Render Occupancy Bar Chart for Reservation Status
    renderOccuppancyBarChart(occupancyData) {
        const viaData = Object.entries(occupancyData).map(([key, value]) => ({ via: key, count: value }));
        this.renderBarChart("occupancyBarChart", viaData, "Occupancy", "via", "count", 'barChartOccupancy');

    }

    // Render Doughnut Chart for Reservation Source
    renderDoughnutChartSource(dataList) {
        const element = document.getElementById("myDoughnutChartSource");
        if (!element) {
            console.error("Doughnut source chart canvas not found");
            return;
        }

        var labels = [];
        var values = [];

        $.each(dataList, function(i, elem){
            labels.push(elem[0]);
            values.push(elem[1]);
        })
//        const chartData = {
//            labels: labels,
//            datasets: [{
//                label: "Reservation Source",
//                data: data,
//                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
//                hoverOffset: 4
//            }]
//        };
//
//        const config = {
//            type: "pie",
//            data: chartData,
//            options: {
//                responsive: true,
//                plugins: {
//                    legend: { position: "bottom" },
//                    title: { display: true, text: "Reservation Source" }
//                }
//            }
//        };

    var ReservationSourceoptions = {
        chart: {
            type: 'pie',
            height: 300,
            dropShadow: {
                enabled: false,
                blur: 5,
                left: 1,
                top: 1,
                opacity: 0.2
            },
            toolbar: {
                show: false
            }
        },
        labels: labels,
        series: values,
        dataLabels: {
            enabled: false
        },
        legend: {
            show: true,
            position: 'bottom',
        },
        stroke: {
            width: 5
        },
        colors: colors,
        fill: {
            type: 'gradient',
            gradient: {
                gradientToColors: light_colors
            }
        }
    }

        if (this.state.doughnutChartSource) {
            this.state.doughnutChartSource.updateOptions(ReservationSourceoptions);
        }
        else{
            this.state.doughnutChartSource = new ApexCharts(element, ReservationSourceoptions);
            this.state.doughnutChartSource.render();
        }

//        this.state.doughnutChartSource = new Chart(ctx, config);
    }

    // Render Doughnut Chart for House Keeping
    renderDoughnutChartHouseKeep(dataList) {
        const element  = document.getElementById("houseKeepingDoughnutChart");
        if (!element ) {
            console.error("Doughnut House Keeping chart not found");
            return;
        }

        var labels = [];
        var values = [];

        $.each(dataList, function(i, elem){
            labels.push(elem[0]);
            values.push(elem[1]);
        })

//        const chartData = {
//            labels: labels,
//            datasets: [{
//                label: "House Keeping",
//                data: data,
//                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
//                hoverOffset: 4
//            }]
//        };
//
//        const config = {
//            type: "pie",
//            data: chartData,
//            options: {
//                responsive: true,
//                plugins: {
//                    legend: { position: "top" },
//                    title: { display: true, text: "House Keeping" }
//                }
//            }
//        };

        var HouseKeepingoptions = {
            chart: {
                type: 'pie',
                height: 300,
                dropShadow: {
                    enabled: false,
                    blur: 5,
                    left: 1,
                    top: 1,
                    opacity: 0.2
                },
                toolbar: {
                    show: false
                }
            },
            labels: labels,
            series: values,
            dataLabels: {
                enabled: false
            },
            legend: {
                show: true,
                position: 'bottom',
            },
            stroke: {
                width: 5
            },
            colors: colors,
            fill: {
                type: 'gradient',
                gradient: {
                    gradientToColors: light_colors
                }
            }
        }

        if (this.state.doughnutChartHouseKeep) {
            this.state.doughnutChartHouseKeep.updateOptions(HouseKeepingoptions);
        }
        else{
            this.state.doughnutChartHouseKeep = new ApexCharts(element, HouseKeepingoptions);
            this.state.doughnutChartHouseKeep.render();
        }
//        this.state.doughnutChartHouseKeep = new Chart(ctx, config);
    }

    renderDoughnutChartOccupied(dataList) {
        const element = document.getElementById("occupiedRoomDoughnutChart");
        if (!element) {
            console.error("Doughnut Occupied / Available Rooms chart canvas not found");
            return;
        }

        var labels = [];
        var values = [];

        $.each(dataList, function(i, elem){
            labels.push(elem[0]);
            values.push(elem[1]);
        })

//        const chartData = {
//            labels: labels,
//            datasets: [{
//                label: "Occupied / Available Rooms",
//                data: data,
//                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
//                hoverOffset: 4
//            }]
//        };
//
//        const config = {
//            type: "pie",
//            data: chartData,
//            options: {
//                responsive: true,
//                plugins: {
//                    legend: { position: "top" },
//                    title: { display: true, text: "Occupied / Available Rooms" }
//                }
//            }
//        };

        var OccupiedRoomoptions = {
            chart: {
                type: 'pie',
                height: 300,
                dropShadow: {
                    enabled: false,
                    blur: 5,
                    left: 1,
                    top: 1,
                    opacity: 0.2
                },
                toolbar: {
                    show: false
                }
            },
            labels: labels,
            series: values,
            dataLabels: {
                enabled: false
            },
            legend: {
                show: true,
                position: 'bottom',
            },
            stroke: {
                width: 5
            },
            colors: colors,
            fill: {
                type: 'gradient',
                gradient: {
                    gradientToColors: light_colors
                }
            }
        }
        if (this.state.doughnutChartOccupiedRoom) {
            this.state.doughnutChartOccupiedRoom.updateOptions(OccupiedRoomoptions);
        }
        else{
            this.state.doughnutChartOccupiedRoom = new ApexCharts(element, OccupiedRoomoptions);
            this.state.doughnutChartOccupiedRoom.render();
        }
//        this.state.doughnutChartOccupiedRoom = new Chart(ctx, config);
    }

    // Display gender and country distribution charts
    displayCounts(genderCounts, countryCounts) {
        const genderData = Object.entries(genderCounts).map(([key, value]) => ({ gender: key, count: value }));
        const countryData = Object.entries(countryCounts).map(([key, value]) => ({ country: key, count: value }));

        this.renderBarChart("genderChart", genderData, "Gender Distribution", "gender", "count");
        this.renderBarChart("countryChart", countryData, "Country Distribution", "country", "count");
    }

    // Render Bar Chart
    renderBarChart(chartId, data, title, labelKey, countKey, stateElement) {
        const element = document.getElementById(chartId);
        if (!element) {
            console.error(`Chart canvas not found: ${chartId}`);
            return;
        }
//
//        const chartData = {
//            labels: data.map(item => item[labelKey]),
//            datasets: [{
//                label: title,
//                data: data.map(item => item[countKey]),
//                backgroundColor: "rgba(24, 69, 139, 0.85)",
//                borderColor: "rgba(75, 192, 192, 1)",
//                borderWidth: 1
//            }]
//        };
//
//        const config = {
//            type: "bar",
//            data: chartData,
//            options: {
//                responsive: true,
//                scales: {
//                    y: { beginAtZero: true }
//                },
//                plugins: {
//                    legend: { position: "top" },
//                    title: { display: true, text: title }
//                }
//            }
//        };
//        this.state[chartId] = new Chart(ctx, config);
        var barChartOptions = {
            chart: {
              height: 350,
              type: 'bar',
            },
            colors: themeColors,
            plotOptions: {
              bar: {
                horizontal: false,
              }
            },
            dataLabels: {
              enabled: false
            },
            series: [{
              data: data.map(item => item[countKey])
            }],
            xaxis: {
              categories: data.map(item => item[labelKey]),
              tickAmount: 5
            },
            yaxis: {
                max: 100,
                labels: {
                    formatter: function (val) {
                        return val.toFixed(0) + "%"; // Affichage du pourcentage sur l'axe Y
                    }
                }
            }
        }

        if (this.state[chartId]){
            this.state[chartId].updateOptions(barChartOptions);
        }
        else{
            this.state[chartId] = new ApexCharts(element, barChartOptions);
            this.state[chartId].render();
        }
    }

    // Display the current bookings
    displayCurrentBookings(currentBookings) {
        const { checked_in: checkedIn, checked_out: checkedOut, in_house: inHouse } = currentBookings;

        const checkedInList = document.getElementById("checkedInList");
        const checkedOutList = document.getElementById("checkedOutList");
        const inHouseList = document.getElementById("inHouseList");

        if (checkedInList) checkedInList.innerHTML = "";
        if (checkedOutList) checkedOutList.innerHTML = "";
        if (inHouseList) inHouseList.innerHTML = "";

        checkedIn.forEach(booking => {
            const listItem = document.createElement("li");
            listItem.classList.add("booking-item");
            listItem.innerHTML = `<div class="booking-info"><strong>${booking[4]}</strong><br><strong>${booking[1]}</strong><br><span>Check-In: ${new Date(booking[2]).toLocaleString()}</span></div>`;
            checkedInList.appendChild(listItem);
        });

        checkedOut.forEach(booking => {
            const listItem = document.createElement("li");
            listItem.classList.add("booking-item");
            listItem.innerHTML = `<div class="booking-info"><strong>${booking[4]}</strong><br><strong>${booking[1]}</strong><br><span>Check-Out: ${new Date(booking[3]).toLocaleString()}</span></div>`;
            checkedOutList.appendChild(listItem);
        });

        inHouse.forEach(booking => {
            const listItem = document.createElement("li");
            listItem.classList.add("booking-item");
            listItem.innerHTML = `<div class="booking-info"><strong>${booking[4]}</strong><br><strong>${booking[1]}</strong><br><span>Check-In: ${booking[2]}</span><br><span>Check-Out: ${booking[3]}</span></div>`;
            inHouseList.appendChild(listItem);
        });
    }


    renderCountryBarChart(countryData) {
        const ctx = document.getElementById('adultsChildrenChart').getContext('2d');

        const countryLabels = countryData.map(item => item.country);
        const totalAdults = countryData.map(item => item.total_adults);
        const totalChildren = countryData.map(item => item.total_children);

        const chartData = {
            labels: countryLabels,
            datasets: [{
                label: 'Total Adults',
                data: totalAdults,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
            }, {
                label: 'Total Children',
                data: totalChildren,
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
            }],
        };

        const config = {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Total Adults and Children by Country',
                    },
                },
            },
        };

        if (this.state.adultsChildrenChart) {
            this.state.adultsChildrenChart.destroy();  // Destroy previous instance if it exists
        }

        this.state.adultsChildrenChart = new Chart(ctx, config);  // Initialize the bar chart
    }


    // Method to load room availability data from the backend
    async loadRoomAvailabilityData() {
            this.state.loading = true;
            var DashboardModel = this.state.DashboardModel;
            var filter_data = this.state.filter_data;

            try {
                // Call the custom method in your model to retrieve room availability
                const roomAvailabilityData = await this.orm.call(DashboardModel, "get_room_available", [], filter_data);
                this.state.roomAvailabilityData = roomAvailabilityData;
            } catch (error) {
                console.error("Failed to load room availability data:", error);
            } finally {
                this.state.loading = false;
            }
        }

    // load Services
    async loadServicesData() {
            this.state.serviceLoading = true;
            var DashboardModel = this.state.DashboardModel;
            var filter_data = this.state.filter_data;
            try {
                // Call the custom method in your model to retrieve room availability
                const servicesData = await this.orm.call(DashboardModel, "get_services", [], filter_data);
                this.state.servicesData = servicesData;
            } catch (error) {
                console.error("Failed to load services data:", error);
            } finally {
                this.state.serviceLoading = false;
            }
        }

    // load Occupancy Table
    async loadOccupyTableData() {
            this.state.occupyLoading = true;
            var DashboardModel = this.state.DashboardModel;
            var filter_data = this.state.filter_data;
            try {
                const occupancyTableData = await this.orm.call(DashboardModel, "get_occupy_table_data", [], filter_data);
                this.state.occupancyTableData = occupancyTableData;
            } catch (error) {
                console.error("Failed to load occupancy Table data:", error);
            } finally {
                this.state.occupyLoading = false;
            }
        }

    // load Occupancy Table
    async loadRatingTableData() {
            this.state.ratingLoading = true;
            var DashboardModel = this.state.DashboardModel;
            var filter_data = this.state.filter_data;
            try {
                const ratingTableData = await this.orm.call(DashboardModel, "get_rating_table_data", [], filter_data);
                this.state.ratingTableData = ratingTableData;
            } catch (error) {
                console.error("Failed to load rating Table data:", error);
            } finally {
                this.state.ratingLoading = false;
            }
        }

    // Render Doughnut Chart for Room Availability
//    renderRoomAvailabilityChart(roomData) {
//        const ctx = document.getElementById("roomAvailabilityChart");
//        if (!ctx) {
//            console.error("Room availability chart canvas not found");
//            return;
//        }
//
//        const roomTypes = roomData.map(row => row.room_type);
//        const availableRooms = roomData.map(row => row.available_rooms);
//
//        const chartData = {
//            labels: roomTypes,
//            datasets: [{
//                label: "Available Rooms",
//                data: availableRooms,
//                backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
//                hoverOffset: 4
//            }]
//        };
//
//        const config = {
//            type: "doughnut",
//            data: chartData,
//            options: {
//                responsive: true,
//                plugins: {
//                    legend: { position: "top" },
//                    title: { display: true, text: "Room Availability Chart" }
//                }
//            }
//        };
//
//        if (this.state.roomAvailabilityChart) {
//            this.state.roomAvailabilityChart.destroy();
//        }
//
//        this.state.roomAvailabilityChart = new Chart(ctx, config);
//    }

       // Define columns for the tree view
    get columns() {
        return [
            { label: _t("Room Type"), key: "room_type" },
            { label: _t("Total Rooms"), key: "total_rooms" },
            { label: _t("Sold Rooms"), key: "sold_rooms" },
            { label: _t("Available Rooms"), key: "available_rooms" },
            { label: _t("Status"), key: "status" },
        ];
    }
}

// Register the component and template
HotelReservationViewDashboard.template = "hotel_dashboard_reservation";
registry.category("actions").add("HotelReservationView", HotelReservationViewDashboard);