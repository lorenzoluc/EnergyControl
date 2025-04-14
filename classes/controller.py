'''
creation of the controller, which can register loads, pv_system and batteries, as well as informing what is registered.
We then have two operational functions, step, which will run a simulation step, basically it will receive everything
that enters and leaves the system, including how much is needed to import/export from the network. If the network limits
are exceeded, a pv limitation is required (proportional to the Pmax of the panels) or a load loss. This function
accepts batteries. The other operational function is battery optimization, given a network profile (load, generation
, grid) it is able to maximize the use of the batteries and return the optimal generation for each step of the
simulation, minimizing the import of energy from the network.
'''


import numpy as np
import cvxpy as cp

class Controller:
    def __init__(self, name):
        self.name = name
        self.loads = []
        self.pvsystems = []
        self.batteries = []

    def register_load(self, load):
        self.loads.append(load)

    def register_pvsystem(self, pvsystem):
        self.pvsystems.append(pvsystem)

    def register_battery(self, battery):
        self.batteries.append(battery)

    def get_registered_devices(self):
        return {
            "loads": [load for load in self.loads],
            "pvsystems": [pv for pv in self.pvsystems],
            "batteries": [battery for battery in self.batteries],
        }

    def step(self,p_max_grid, timestamp=None,):
        """
        Run a step of simulation or real-time
        """
        if p_max_grid <= 0:
            raise ValueError("p_max_grid (Power to/from grid) must be positive")
        if timestamp is not None and (timestamp < 0 or not isinstance(timestamp, int)):
            raise ValueError("Timestamp must be integer positive")

        total_load = 0
        total_pv   = 0
        total_bat  = 0
        total_bat_available = 0

        for load in self.loads:
            load.set_time(timestamp)
            total_load += load.get_power()

        for pvsystem in self.pvsystems:
            pvsystem.set_time(timestamp)
            total_pv += pvsystem.get_power()

        for battery in self.batteries:
            battery.set_time(timestamp)
            total_bat += battery.get_power()


        #Grid power
        power_balance = total_pv + total_bat - total_load #+ to the grid, - from the grid
        if power_balance >= 0:
            p_to_grid = min(power_balance, p_max_grid)
            p_from_grid = 0
            unmet_load = 0
        else:
            remaining_load = -power_balance
            p_from_grid = min(remaining_load, p_max_grid)
            p_to_grid = 0
            unmet_load = remaining_load - p_from_grid

        print(f"\n[{self.name}] t={timestamp} | Load={total_load:.2f} W | PV={total_pv:.2f} W | Batterie={total_bat:.2f} W | Grid(+out/-in)={p_to_grid - p_from_grid:.2f} W")


        # Operation of the controller
        pvs_cmd = []
        if power_balance > p_max_grid:  # Need of limitation. then -> actual production - the excess
            excess_power = power_balance - p_max_grid
            print(f"Excess generation detected: {excess_power:.2f} W — limiting PVs proportionally:")
            for pvsystem in self.pvsystems:
                pv_power = pvsystem.get_power()
                share = pv_power / total_pv if total_pv > 0 else 0
                pv_cmd = pv_power - (excess_power * share)
                pvs_cmd.append(pv_cmd)
                pvsystem.p_max_pv_cmd = pv_cmd
                print(f"PV_System : {pvsystem.name} limited to {pv_cmd:.2f} W.  {excess_power * share:.2f} W of production limited.")
        elif power_balance < p_max_grid and power_balance < 0:
            for pvsystem in self.pvsystems:
                pv_cmd = pvsystem.p_pv
                pvs_cmd.append(pv_cmd)
            print(f"Unmet load: {unmet_load:.2f} W.")
        else:
            for pvsystem in self.pvsystems:
                pv_cmd = pvsystem.p_pv
                pvs_cmd.append(pv_cmd)


        return timestamp, total_load, total_pv, total_bat, (p_to_grid - p_from_grid), pv_cmd


    def optimization_battery(self,timesteps,p_grid):
        if p_grid <= 0:
            raise ValueError("p_max_grid (Power to/from grid) must be positive")
        if timesteps is not None and (timesteps < 0 or not isinstance(timesteps, int)):
            raise ValueError("Timestamp must be integer positive")


        #Load and PV
        load_list = timesteps*[0]
        pv_list = timesteps*[0]


        for time in range(timesteps):
            for load in self.loads:
                load.set_time(time)
                load_list[time] += load.get_power()
            for pvsystem in self.pvsystems:
                pvsystem.set_time(time)
                pv_list[time] += pvsystem.get_power()

        #variables of each battery
        batteries = self.batteries
        nb = len(batteries)

        c = [cp.Variable(timesteps) for _ in range(nb)]  # charge of battery
        d = [cp.Variable(timesteps) for _ in range(nb)]  # discharge of battery
        s = [cp.Variable(timesteps) for _ in range(nb)]  # soc of battery
        g = cp.Variable(timesteps)  # energy from grid
        slack = cp.Variable(timesteps) #Unsuplied energy
        pv_curtail = cp.Variable(timesteps) #curtailment

        #restrictions
        constraints = []

        for i, battery in enumerate(batteries):
            soc0 = battery.soc_bess * battery.p_bess
            capacity = battery.p_bess
            max_charge = battery.max_charge
            max_discharge = battery.max_discharge
            eta = battery.eta

            constraints += [s[i][0] == soc0]
            constraints += [s[i][-1] == soc0]

            for t in range(timesteps):
                # SOC evolution: soc in time t+1 should be equal to soc in time t + the charge/discharge of the battery
                if t != 23:
                    constraints += [s[i][t + 1] == s[i][t] + eta * c[i][t] - d[i][t] / eta]

                # physical limits: not charge/discharge more than the limit neither from the capacity
                constraints += [0 <= c[i][t], c[i][t] <= max_charge]
                constraints += [0 <= d[i][t], d[i][t] <= max_discharge]
                constraints += [0 <= s[i][t], s[i][t] <= capacity]
                constraints += [cp.abs(g[t]) <= p_grid]

                total_charge = sum(c[i][t] for i in range(nb))
                total_discharge = sum(d[i][t] for i in range(nb))
                constraints += [
                    pv_list[t] - pv_curtail[t] + total_discharge + g[t] + slack[t] == load_list[t] + total_charge
                ]
                constraints.append(pv_curtail[t] >= 0)
                constraints.append(slack[t] >= 0)



        # goal: minimize the energy imported from the network
        objective = cp.Minimize(cp.sum(g) + 1e6 * cp.sum(slack) + 10 * cp.sum(pv_curtail))
        prob = cp.Problem(objective, constraints)
        prob.solve(solver=cp.ECOS)
        print("Battery optimization. Status:", prob.status)


        return {
            "grid_import": g.value,
            "slack": slack.value,
            "curtailment":pv_curtail.value,
            "battery_charge": [ci.value for ci in c],
            "battery_discharge": [di.value for di in d],
            "battery_soc": [si.value for si in s]
        }