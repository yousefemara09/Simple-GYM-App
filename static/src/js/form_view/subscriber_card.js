/* @odoo-module */

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SubscriberCard extends Component {
    static template = "gym_app.FormView";
    static props = { onCreated: Function };
    setup() {
        this.orm = useService("orm");
        this.form = useState({
            name: "",
            phone: "",
        });
    }
    async create_data() {
        await this.orm.create("subscriber", [
            {
                name: this.form.name,
                phone: this.form.phone,
            },
        ]);
        this.form.name = "";
        this.form.phone = "";
        this.props.onCreated();
    }

    cancel() {
        this.props.onCreated();
    }
}
