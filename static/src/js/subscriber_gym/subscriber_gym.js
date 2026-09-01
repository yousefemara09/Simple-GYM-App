/* @odoo-module */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { SubscriberCard } from "../form_view/subscriber_card";

export class SubscriberGym extends Component {
    static template = "gym_app.SubscriberGymList";
    static components = { SubscriberCard };
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            records: [],
            showCreate: false,
        });
        this.created_successfully = this.created_successfully.bind(this);
        this.loadData();
    }

    async loadData() {
        const result = await this.orm.searchRead(
            "subscriber",
            [],
            ["id", "ref", "name", "phone"]
        );
        this.state.records = result;
    }

    open_create() {
        this.state.showCreate = true;
    }

    created_successfully() {
        this.state.showCreate = false;
        this.loadData();
    }

    async delete_data(id) {
        await this.orm.unlink("subscriber", [id]);
        await this.loadData();
    }
}

registry.category("actions").add("gym_app.subscriber_gym", SubscriberGym);
