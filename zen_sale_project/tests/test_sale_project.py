from odoo.tests.common import TransactionCase

class TestSaleOrder(TransactionCase):

    def test_create_project_and_tasks(self):
        """Test creation of project and tasks for sale order"""

        # Create a partner for the sale order
        partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test.partner@example.com',
        })

        # Create a sale order with one order line
        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {
                'product_id': self.env.ref('product.product_product_1').id,
                'name': 'Test Product',
                'product_uom_qty': 10,
                'price_unit': 100.0,
            })],
        })

        # Check that the project and tasks were created
        self.assertEqual(len(order.project_ids), 1, "Project not created for sale order")
        project = order.project_ids[0]
        self.assertEqual(project.name, f"Project for Sale Order {order.name}", "Project name not set correctly")
        self.assertEqual(len(project.task_ids), 1, "Tasks not created for project")
        task = project.task_ids[0]
        self.assertEqual(task.name, "Test Product", "Task name not set correctly")
        self.assertEqual(task.planned_hours, 10.0, "Task planned hours not set correctly")
        self.assertEqual(task.stage_id.name, "To Do", "Task stage not set correctly")
