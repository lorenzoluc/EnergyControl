import unittest
from unittest.mock import MagicMock
from classes.controller import Controller
import numpy as np


class TestController(unittest.TestCase):

    def setUp(self):
        self.controller = Controller(name="Test Controller")

        # Mocking devices
        self.load_mock = MagicMock()
        self.pvsystem_mock = MagicMock()
        self.battery_mock = MagicMock()

        # Setting up mock behaviors for methods
        self.load_mock.get_power.return_value = 10
        self.pvsystem_mock.get_power.return_value = 5
        self.battery_mock.get_power.return_value = 2

        # Registering devices
        self.controller.register_load(self.load_mock)
        self.controller.register_pvsystem(self.pvsystem_mock)
        self.controller.register_battery(self.battery_mock)

    def test_register_devices(self):
        # Test if devices are registered properly
        registered_devices = self.controller.get_registered_devices()
        self.assertIn(self.load_mock, registered_devices["loads"])
        self.assertIn(self.pvsystem_mock, registered_devices["pvsystems"])
        self.assertIn(self.battery_mock, registered_devices["batteries"])

    def test_step_computations(self):
        # Mocking power values for devices at a specific timestamp
        self.controller.step(p_max_grid=10, timestamp=1)

        # Assert power calculations and grid interactions are correct
        self.load_mock.set_time.assert_called_with(1)
        self.pvsystem_mock.set_time.assert_called_with(1)
        self.battery_mock.set_time.assert_called_with(1)

        # Checking if the power balance and grid values are being computed
        # assuming the formula: power_balance = total_pv + total_bat - total_load
        expected_power_balance = 5 + 2 - 10
        self.assertEqual(self.controller.step(10, timestamp=1)[4], expected_power_balance) #p_to_grid - p_from_grid

    def test_step_power_balance_limit(self):
        # Case where power balance exceeds max grid
        self.pvsystem_mock.get_power.return_value = 50  # PV generating more than load
        self.battery_mock.get_power.return_value = 10  # Battery also producing power
        self.load_mock.get_power.return_value = 20  # Load consumption

        # Run the step function
        result = self.controller.step(p_max_grid=20, timestamp=1)

        # Check that PV is limited to avoid exceeding grid limits
        self.assertEqual(result[4], 20)  # Exporting the max of the Grid

    def test_step_unmet_load(self):
        # Case where the grid needs to supply power due to unmet load
        self.pvsystem_mock.get_power.return_value = 5
        self.battery_mock.get_power.return_value = 0
        self.load_mock.get_power.return_value = 15  # Excess load

        result = self.controller.step(p_max_grid=10, timestamp=1)

        # Check if the grid is providing power
        self.assertEqual(result[4], -10)  # Grid interaction should be 10W (import)

    def test_optimization_battery(self):
        #TODO Check optimization contraints

        # Setting up mock battery details for optimization
        self.battery_mock.soc_bess = 0.8
        self.battery_mock.p_bess = 10
        self.battery_mock.max_charge = 5
        self.battery_mock.max_discharge = 5
        self.battery_mock.eta = 0.95

        # Mocking the behavior for the battery during optimization
        self.controller.optimization_battery(timesteps=24, p_grid=10)

        # Testing if optimization function was called and expected optimization result is present
        self.assertTrue(self.controller.optimization_battery(timesteps=24, p_grid=10))


if __name__ == "__main__":
    unittest.main()