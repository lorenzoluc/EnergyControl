Energy Control
This repository provides a simple yet extensible Python framework for simulating energy flows in a low-voltage electrical network with distributed energy resources (DERs), including photovoltaic systems, loads, and batteries. It includes simulation-time modeling, a basic rule-based controller, and an optimization module for battery dispatch using cvxpy.

🧱 Components
1. Elements
A base class shared by all grid-connected elements. It includes:

name and controller association

Time-stepping simulation (set_time, advance_time)

Basic power output interface (get_power)

2. Pv_system
Represents a photovoltaic system with:

Nominal installed power (p_pv)

Scalable production profile (0 to 1 normalized)

Optional curtailment control (p_max_pv_cmd)

Automatic registration with controller

3. Load
Represents a load with:

Nominal power (p_load)

Scalable consumption profile (0 to 1 normalized)

Automatic registration with controller

4. Battery
Represents a battery energy storage system with:

Power capacity (p_bess)

Initial SOC (soc_bess)

Charging/discharging limits and round-trip efficiency

Optional dispatch profile

Automatic registration with controller

🧠 Controller
The Controller manages all elements and performs operational logic:

✅ Registration
Supports dynamic registration of:

Loads

PV systems

Batteries

🔁 Step Simulation
Simulates a single timestep:

Calculates power balance between generation, load, battery, and grid

Applies PV curtailment if necessary

Reports unmet demand

⚙️ Battery Optimization
Implements a convex optimization strategy (via cvxpy) to:

Minimize energy imported from the grid

Schedule battery charge/discharge

Handle curtailment and load slack

Comply with physical constraints (SOC bounds, efficiency, etc.)

📊 Usage
In main.py:

Create time-series for PV generation, load, and optionally battery profiles.

Instantiate controller and grid elements.

Simulate time steps or run battery optimization.