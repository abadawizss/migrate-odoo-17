console.log('Load.................................................................!');

odoo.define('zen_sale_project.my_widget', function (require) {
    "use strict";

    console.log('Before Widget.................................................................!');

    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var core = require('web.core');

    $(document).on('click', '#my-button', function(){
        console.log("Button clicked");

        var task_id = self.id
        var record_id = this.dataset.resId;

        var formController = this.formView.controller;
        var recordId = formController.getCurrentId();

        console.log("ID:", recordId);
        console.log("Current record ID:", record_id);

        console.log("Task ID:", task_id);

//        var task_id = 9;  // Replace with the ID of the project task that you want to update
        console.log("Task ID:", task_id);
        var stage_id = 3;  // Replace with the ID of the stage that you want to set for the project task

        // Update the task stage
        rpc.query({
            model: 'project.task',
            method: 'write',
            args: [[task_id], {'stage_id': stage_id}]
        }).then(function(result) {
            console.log("Task stage updated successfully");

            // Add console log to confirm that stage was updated
            rpc.query({
                model: 'project.task',
                method: 'read',
                args: [[task_id], ['stage_id']]
            }).then(function(result) {
                console.log("Task stage is now:", result[0].stage_id[1]);
            }).catch(function(error) {
                console.log("Error occurred while reading task stage:", error);
            });
        }).catch(function(error) {
            console.log("Error occurred while updating task stage:", error);
        });
    });
});