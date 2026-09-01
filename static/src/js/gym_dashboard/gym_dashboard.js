/* @odoo-module */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class GymDashboard extends Component {
    static template = "gym_app.gymDashboard";
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            subscribers: [],
            searchQuery: "",
            currentPage: 1,
            filterState: "all",
        });
        onWillStart(async () => {
            await this.loadData();
        });
    }
    async loadData() {
        this.state.subscribers = await this.orm.searchRead("subscriber",
            [],
            ["id", "ref", "name", "phone", "state"]
        );
    }
    get totalSubscribers() {
        return this.state.subscribers.length;
    }
    get activeSubscribers() {
        return this.state.subscribers.filter(sub => sub.state == 'active').length;
    }
    get expiredSubscribers() {
        return this.state.subscribers.filter(sub => sub.state == 'expired').length;
    }
    onSearchInput(ev) {
        this.state.searchQuery = ev.target.value;
    }
    setFilter(ev) {
        this.state.filterState = ev.target.value;
    }

    get SearchedFilterSubscribers() {
        const query = this.state.searchQuery.toLowerCase().trim();
        const state = this.state.filterState;
        const result = this.state.subscribers.filter((sub) => {
            if (query === "") { return true; }
            if (state !== "all") { if (sub.state !== state) { return false; } }
            if (sub.name) { if (sub.name.toLowerCase().includes(query)) { return true; } }
            if (sub.ref) { if (sub.ref.toLowerCase().includes(query)) { return true; } }
            if (sub.phone) { if (sub.phone.toLowerCase().includes(query)) { return true; } }
            return false;
        });
        return result;
    }
    get totalPages() {
        const totalPage = this.SearchedFilterSubscribers.length;
        const pageSize = 5;
        return Math.ceil(totalPage / pageSize);
    }
    get CurrentPageSubscribers() {
        const pageSize = 5;
        const start = (this.state.currentPage - 1) * pageSize;
        const end = start + pageSize;
        return this.SearchedFilterSubscribers.slice(start, end);
    }
    previousPage() {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
        }
    }
    nextPage() {
        if (this.state.currentPage < this.totalPages) {
            this.state.currentPage++;
        }
    }
}
registry.category("actions").add("gym_app.dashboard_gym", GymDashboard);
