'''
Creation of network elements. First, Elements which is generic and allows us to create common attributes such as name,
controller, and simulation functions such as get_power, set_time and advance_time. These functions are solely for
simulation but can be adapted to real time. Next is the pv_system, with information on the nominal power, limiting
power, a profile and the method of subscribing to a controller. Then there's load, with a pmax, a profile and entry in
the controller. Finally, we have the battery with information on pmax, profile, initial SOC, SOC profile, maximum
charge/discharge rate, eta and profile.
'''


class Elements():
    def __init__(self,name,controller):
        self.name = name
        self.controller = controller
        self.profile = []

    def get_power(self):
        if self._t < len(self.profile):
            return self.profile[self._t]
        return 0

    def set_time(self,time):
        self._t = time

    def advance_time(self):
        self._t += 1

class Pv_system(Elements):
    def __init__(self,name,controller,p_pv,profile=None):
        if p_pv <= 0:
            raise ValueError("p_pv (PV max power) must be positive")
        if profile is not None and any(p < 0 or p > 1 for p in profile):
            raise ValueError("PV profile values must be between 0 and 1")


        super().__init__(name, controller)

        self._profile = [x * p_pv for x in profile] if profile is not None else []
        self._p_pv = p_pv
        self._p_max_pv_cmd = self.p_pv

        self.register()

    @property
    def p_pv(self):
        return self._p_pv

    @p_pv.setter
    def p_pv(self, value):
        if value <= 0:
            raise ValueError("p_pv (PV max power) must be positive")
        self._p_pv = value

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, value):
        if value is None:
            self._profile = []
        elif any(p < 0 or p> 1 for p in value):
            raise ValueError("PV profile values must be between 0 and 1")
        else:
            self._profile = [x * self.p_pv for x in value]

    @property
    def p_max_pv_cmd(self):
        return self._p_max_pv_cmd

    @p_max_pv_cmd.setter
    def p_max_pv_cmd(self, value):
        if value < 0 or value > self.p_pv:
            raise ValueError("p_max_pv_cmd must be between 0 and p_pv")
        self._p_max_pv_cmd = value

    def register(self):
        self.controller.register_pvsystem(self)

class Load(Elements):
    def __init__(self,name,controller,p_load,profile=None):
        if p_load <= 0:
            raise ValueError("p_load (Load max power) must be positive")
        if profile is not None and any(p < 0 or p > 1 for p in profile):
            raise ValueError("Load profile values must be between 0 and 1")


        super().__init__(name, controller)

        self._p_load = p_load
        self._profile = [x * p_load for x in profile] if profile is not None else []

        self.register()

    @property
    def p_load(self):
        return self._p_load

    @p_load.setter
    def p_load(self, value):
        if value <= 0:
            raise ValueError("p_load must be positive")
        self._p_load = value

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, values):
        if values is not None and any(p < 0 or p> 1 for p in values):
            raise ValueError("Profile values must be between 0 and 1")
        elif values is None:
            self._profile = []
        else:
            self._profile = [p * self.p_load for p in values]

    def register(self):
        self.controller.register_load(self)

class Battery(Elements):
    def __init__(self,name,controller,p_bess,soc_bess=None,profile=None):
        if p_bess <= 0:
            raise ValueError("p_bess must be positive")
        if profile is not None and any(p < -1 or p > 1 for p in profile):
            raise ValueError("Load profile values must be between -1 and 1")
        if soc_bess is not None and not (0 <= soc_bess <= 1):
            raise ValueError("soc_bess must be between 0 and 1")

        super().__init__(name, controller)

        self._p_bess = p_bess
        self._profile = [x * p_bess for x in profile] if profile is not None else []
        self._soc_bess = soc_bess if soc_bess is not None else 0.7


        self.soc_profile = []
        self.max_charge = 10
        self.max_discharge = 10
        self.eta = 0.95

        self.register()

    @property
    def p_bess(self):
        return self._p_bess

    @p_bess.setter
    def p_bess(self, value):
        if value <= 0:
            raise ValueError("p_bess must be positive")
        self._p_bess = value

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, values):
        if any(p < -1 or p > 1 for p in values):
            raise ValueError("All profile values must be between -1 and 1")
        self._profile = [p * self.p_bess for p in values]

    @property
    def soc_bess(self):
        return self._soc_bess

    @soc_bess.setter
    def soc_bess(self, value):
        if not (0 <= value <= 1):
            raise ValueError("soc_bess must be between 0 and 1")
        self._soc_bess = value

    def register(self):
        self.controller.register_battery(self)

    def get_soc(self):
        if self._t < len(self.soc_profile):
            return self.soc_profile[self._t]
        return 0


