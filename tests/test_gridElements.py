import unittest
from unittest import mock
from classes.gridElements import *


class TestBattery(unittest.TestCase):

    def setUp(self):
        self.controller_mock = unittest.mock.Mock()  # Mocking the controller for testing
        self.battery = Battery(name="Test Battery", controller=self.controller_mock, p_bess=10)

    def test_initialization_with_valid_p_bess(self):
        battery = Battery(name="Test Battery", controller=self.controller_mock, p_bess=10)
        self.assertEqual(battery.p_bess, 10)
        self.assertEqual(battery.soc_bess, 0.7)
        self.assertEqual(battery.profile, [])

    def test_initialization_with_invalid_p_bess(self):
        with self.assertRaises(ValueError):
            Battery(name="Test Battery", controller=self.controller_mock, p_bess=-5)

    def test_profile_validation_on_initialization(self):
        # Valid profile
        battery = Battery(name="Test Battery", controller=self.controller_mock, p_bess=10, profile=[0.5, 0.8, 0.9])
        self.assertEqual(battery.profile, [5.0, 8.0, 9.0])

        # Invalid profile
        with self.assertRaises(ValueError):
            Battery(name="Test Battery", controller=self.controller_mock, p_bess=10, profile=[1.2, -0.5, 0.9])

    def test_soc_bess_validation_on_initialization(self):
        battery = Battery(name="Test Battery", controller=self.controller_mock, p_bess=10, soc_bess=0.8)
        self.assertEqual(battery.soc_bess, 0.8)

        with self.assertRaises(ValueError):
            Battery(name="Test Battery", controller=self.controller_mock, p_bess=10, soc_bess=1.2)

        with self.assertRaises(ValueError):
            Battery(name="Test Battery", controller=self.controller_mock, p_bess=10, soc_bess=-0.2)

    def test_set_time(self):
        self.battery.set_time(5)
        self.assertEqual(self.battery._t, 5)

    def test_get_soc(self):
        self.battery.set_time(0)
        self.battery.soc_profile = [0.7, 0.8, 1.0]
        self.assertEqual(self.battery.get_soc(), 0.7)

        self.battery.set_time(2)
        self.assertEqual(self.battery.get_soc(), 1.0)

        self.battery.set_time(5)  # Beyond profile length
        self.assertEqual(self.battery.get_soc(), 0)

    def test_advance_time(self):
        self.battery.set_time(0)
        self.battery.advance_time()
        self.assertEqual(self.battery._t, 1)

    def test_profile_setter_with_invalid_values(self):
        with self.assertRaises(ValueError):
            self.battery.profile = [1.2, 0.8, -0.3]  # Invalid profile values

    def test_profile_setter_with_valid_values(self):
        self.battery.profile = [0.5, 0.7, 0.9]
        self.assertEqual(self.battery.profile, [5.0, 7.0, 9.0])

    def test_p_bess_setter_valid_value(self):
        # Test setting p_bess to a valid positive value
        self.battery.p_bess = 15
        self.assertEqual(self.battery.p_bess, 15)

    def test_p_bess_setter_invalid_value(self):
        # Test setting p_bess to an invalid (non-positive) value
        with self.assertRaises(ValueError):
            self.battery.p_bess = -1  # Should raise ValueError
        with self.assertRaises(ValueError):
            self.battery.p_bess = 0  # Should also raise ValueError

    def test_soc_bess_setter_valid_value(self):
        # Test setting soc_bess to a valid value
        self.battery.soc_bess = 0.85
        self.assertEqual(self.battery.soc_bess, 0.85)

    def test_soc_bess_setter_invalid_value(self):
        # Test setting soc_bess to an invalid value (out of range)
        with self.assertRaises(ValueError):
            self.battery.soc_bess = -0.1  # Should raise ValueError
        with self.assertRaises(ValueError):
            self.battery.soc_bess = 1.2  # Should raise ValueError

    def test_register_called_on_initialization(self):
        self.controller_mock.register_battery.assert_called_once_with(self.battery)


class TestLoad(unittest.TestCase):
    def setUp(self):
        self.controller_mock = unittest.mock.Mock()  # Mocking the controller for testing
        self.load = Load(name="Test load", controller=self.controller_mock, p_load=10)

    def test_initialization_p_load(self):
        load = Load(name="Test load", controller=self.controller_mock, p_load=10)
        self.assertEqual(load.p_load, 10)
        self.assertEqual(load.profile, [])

        with self.assertRaises(ValueError):
            load = Load(name="Test load", controller=self.controller_mock, p_load=-5)

    def test_profile_validation_on_initialization(self):
        # Valid profile
        load = Load(name="Test Load", controller=self.controller_mock, p_load=10, profile=[0.5, 0.8, 0.9])
        self.assertEqual(load.profile, [5.0, 8.0, 9.0])

        # Invalid profile
        with self.assertRaises(ValueError):
            Load(name="Test Load", controller=self.controller_mock, p_load=10, profile=[1.2, -0.5, 0.9])

    def test_set_time(self):
        self.load.set_time(5)
        self.assertEqual(self.load._t, 5)

    def test_advance_time(self):
        self.load.set_time(0)
        self.load.advance_time()
        self.assertEqual(self.load._t, 1)

    def test_get_power(self):
        self.load.set_time(0)
        self.load.profile = [0.5, 0.7, 1.0]
        self.assertEqual(self.load.get_power(), 5)

        self.load.set_time(2)
        self.assertEqual(self.load.get_power(), 10)

        self.load.set_time(5)  # Beyond profile length
        self.assertEqual(self.load.get_power(), 0)

    def test_profile_setter_with_none(self):
        self.load.profile = None
        self.assertEqual(self.load.profile, [])

    def test_profile_setter_with_invalid_values(self):
        with self.assertRaises(ValueError):
            self.load.profile = [1.2, 0.8, -0.3]  # Invalid profile values

    def test_register_called_on_initialization(self):
        self.controller_mock.register_load.assert_called_once_with(self.load)

    def test_p_pv_setter_value(self):
        # Test setting p_pv to a valid positive value
        self.load.p_load = 15
        self.assertEqual(self.load.p_load, 15)

        with self.assertRaises(ValueError):
            self.load.p_load = -1  # Should raise ValueError
        with self.assertRaises(ValueError):
            self.load.p_load = 0  # Should also raise ValueError


class TestPvSystem(unittest.TestCase):

    def setUp(self):
        self.controller_mock = unittest.mock.Mock()  # Mocking the controller for testing
        self.pv_system = Pv_system(name="Test PV System", controller=self.controller_mock, p_pv=10)

    def test_initialization_p_pv(self):
        pv_system = Pv_system(name="Test PV System", controller=self.controller_mock, p_pv=10)
        self.assertEqual(pv_system.p_pv, 10)
        self.assertEqual(pv_system.profile, [])

        with self.assertRaises(ValueError):
            Pv_system(name="Test PV System", controller=self.controller_mock, p_pv=-5)


    def test_profile_validation_on_initialization(self):
        # Valid profile
        pv_system = Pv_system(name="Test PV System", controller=self.controller_mock, p_pv=10, profile=[0.5, 0.8, 0.9])
        self.assertEqual(pv_system.profile, [5.0, 8.0, 9.0])

        # Invalid profile
        with self.assertRaises(ValueError):
            Pv_system(name="Test PV System", controller=self.controller_mock, p_pv=10, profile=[1.2, -0.5, 0.9])

    def test_set_time(self):
        self.pv_system.set_time(5)
        self.assertEqual(self.pv_system._t, 5)

    def test_get_power(self):
        self.pv_system.set_time(0)
        self.pv_system.profile = [0.5, 0.7, 1.0]
        self.assertEqual(self.pv_system.get_power(), 5)

        self.pv_system.set_time(2)
        self.assertEqual(self.pv_system.get_power(), 10)

        self.pv_system.set_time(5)  # Beyond profile length
        self.assertEqual(self.pv_system.get_power(), 0)

    def test_advance_time(self):
        self.pv_system.set_time(0)
        self.pv_system.advance_time()
        self.assertEqual(self.pv_system._t, 1)

    def test_profile_setter_with_none(self):
        self.pv_system.profile = None
        self.assertEqual(self.pv_system.profile, [])

    def test_profile_setter_with_invalid_values(self):
        with self.assertRaises(ValueError):
            self.pv_system.profile = [1.2, 0.8, -0.3]  # Invalid profile values

    def test_p_max_pv_cmd_setter(self):
        self.pv_system.p_max_pv_cmd = 5
        self.assertEqual(self.pv_system.p_max_pv_cmd, 5)

    def test_p_max_pv_cmd_setter_with_invalid_value(self):
        with self.assertRaises(ValueError):
            self.pv_system.p_max_pv_cmd = -5  # Invalid value (negative)
        with self.assertRaises(ValueError):
            self.pv_system.p_max_pv_cmd = 15  # Invalid value (greater than p_pv)

    def test_register_called_on_initialization(self):
        self.controller_mock.register_pvsystem.assert_called_once_with(self.pv_system)

    def test_p_pv_setter_value(self):
        # Test setting p_pv to a valid positive value
        self.pv_system.p_pv = 15
        self.assertEqual(self.pv_system.p_pv, 15)

        with self.assertRaises(ValueError):
            self.pv_system.p_pv = -1  # Should raise ValueError
        with self.assertRaises(ValueError):
            self.pv_system.p_pv = 0  # Should also raise ValueError



if __name__ == "__main__":
    unittest.main()