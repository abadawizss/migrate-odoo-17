console.log('Load.................................................................!');

odoo.define('zen_sale_project.my_widget', function (require) {
    "use strict";

    console.log('Before Widget.................................................................!');

    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var MyWidget = Widget.extend({
        events: {
            'click #my-button': '_onClickMyButton',
        },

        _onClickMyButton: function (ev) {
            ev.preventDefault();
            console.log("Button clicked");

            var task_id = 1;  // Replace with the ID of the project task that you want to update
            console.log("Task ID:", task_id);
            var stage_id = 30;  // Replace with the ID of the stage that you want to set for the project task

            var params = [[task_id], {'stage_id': stage_id}];
            var kwargs = {context: session.user_context};

            rpc.query({
                model: 'project.task',
                method: 'write',
                args: params,
                kwargs: kwargs,
            }).then(function(result) {
                console.log("Task stage updated successfully");

                rpc.query({
                    model: 'project.task',
                    method: 'read',
                    args: [[task_id], ['stage_id']],
                    kwargs: kwargs,
                }).then(function(result) {
                    console.log("Task stage is now:", result[0].stage_id[1]);
                }).catch(function(error) {
                    console.log("Error occurred while reading task stage:", error);
                });
            }).catch(function(error) {
                console.log("Error occurred while updating task stage:", error);
            });
        },
    });

    return MyWidget;
});


console.log('Load.................................................................!');

odoo.define('zen_sale_project.my_widget', function (require) {
    "use strict";

    console.log('Before Widget.................................................................!');

    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    $(document).on('click', '#my-button', function(){
        console.log("Button clicked");

        var task_id = 40;  // Replace with the ID of the project task that you want to update
        console.log("Task ID:", task_id);
        var stage_id = 3;  // Replace with the ID of the stage that you want to set for the project task

        // Update the task stage using sudo method to bypass access rights
        rpc.query({
            model: 'project.task',
            method: 'sudo',
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

                // Send request to Python function to update task stage
                $.ajax({
                        url: '/update_task_stage',
                        type: 'POST',
                        dataType: 'json',
                        data: {
                            task_id: task_id,
                            stage_id: stage_id,
                        },
                        success: function(result) {
                            console.log("Task stage updated successfully");
                        },
                        error: function(xhr, status, error) {
                            console.log("Error occurred while updating task stage:", error);
                        },
                });

            }).catch(function(error) {
                console.log("Error occurred while reading task stage:", error);
            });
        }).catch(function(error) {
            console.log("Error occurred while updating task stage:", error);
        });
    });
});