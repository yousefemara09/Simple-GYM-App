from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestGym(TransactionCase):

    def setUp(self):
        super().setUp()
        self.test_subscriber = self.env['subscriber'].create({
            'name': 'Test Subscriber',
            'phone': '010000',
        })
        self.test_package = self.env['package'].create({
            'name': 'Test Package',
            'price': 122.5,
            'months': '3-months',
        })

    def test_subscriber_create(self):
        self.assertRecordValues(self.test_subscriber,
            [{
                'name': 'Test Subscriber',
                'phone': '010000',
            }]
        )

    def test_package_create(self):
        self.assertRecordValues(self.test_package,
            [{
                'name': 'Test Package',
                'price': 122.5,
                'months': '3-months',
            }]
        )

    def test_sequence_create(self):
        self.assertNotEqual(self.test_subscriber.ref, 'New')
        self.assertTrue(self.test_subscriber.ref.startswith('SUB'))

    def test_related_price(self):
        sub = self.env['subscriber'].create({
            'name': 'Test Subscriber',
            'phone': '010000',
            'package_id': self.test_package.id,
        })
        self.assertEqual(sub.price, 122.5)

    def test_check_price(self):
        with self.assertRaises(ValidationError):
            self.env['package'].create({
                'name': 'Test Package',
                'price': -122.5,
                'months': '3-months',
            })

    def test_smart_button(self):
        subscriber = self.env['subscriber'].create({
            'name': 'Ahmed',
            'package_id': self.test_package.id,
        })
        action = self.test_package.get_all_sub()
        self.assertEqual(action['domain'], [('package_id', '=', self.test_package.id)])

    def test_server(self):
        subscriber = self.env['subscriber'].create({
            'name': 'Test Subscriber',
            'phone': '010000',
            'state': 'active',
        })
        subscriber.action_server_expire_subscriber()
        self.assertEqual(subscriber.state, 'expired')

    def test_renew_wizard(self):
        subscriber = self.env['subscriber'].create({
            'name': 'Test Subscriber',
            'phone': '010000',
            'package_id': self.test_package.id,
        })
        wizard = self.env['renew.wizard'].create({
            'name': 'Renewal',
            'subscriber_id': subscriber.id,
            'months': 2,
        })
        wizard.action_confirm()
        self.assertEqual(subscriber.state, 'active')
        self.assertTrue(subscriber.end_date)
