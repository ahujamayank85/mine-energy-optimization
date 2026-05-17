import os
os.environ["POLARS_SKIP_CPU_CHECK"] = "1"

import pypsa
import pandas as pd
import matplotlib.pyplot as plt

# 1. Initialize Network
network = pypsa.Network()
snapshots = pd.date_range("2026-01-01 00:00", "2026-12-31 23:00", freq="h")
network.set_snapshots(snapshots)

# 2. Define Carriers
network.add("Carrier", "electricity")
network.add("Carrier", "diesel")

# 3. Add Buses
network.add("Bus", "Mine Electricity Bus", carrier="electricity")
network.add("Bus", "Mine Diesel Bus", carrier="diesel")

# 4. Add Demands (Loads)
elec_base = [15, 14, 14, 15, 18, 22, 25, 25, 24, 22, 20, 20, 18, 18, 20, 22, 24, 25, 22, 20, 18, 16, 15, 15]
diesel_base = [5, 5, 4, 4, 8, 10, 12, 12, 10, 10, 8, 8, 8, 9, 11, 12, 12, 10, 8, 6, 5, 5, 5, 5]

elec_demand = elec_base * 365
diesel_demand = diesel_base * 365

network.add("Load", "Electrical Load", bus="Mine Electricity Bus", p_set=elec_demand)
network.add("Load", "HEMM Diesel Load", bus="Mine Diesel Bus", p_set=diesel_demand)

# 5. Add Generation Infrastructure (with optimized cost ratios)
network.add("Generator", "Diesel Supply Source", bus="Mine Diesel Bus", efficiency=1.0, marginal_cost=90, p_nom_extendable=True)

# Utility Grid: Set up as a highly available backup option
network.add("Generator", "Utility Grid", bus="Mine Electricity Bus", 
            p_nom=25,               # Raised to 25 MW to fully cover mine peak load if needed
            marginal_cost=50,       # Adjusted tariff relative to asset capital expenditures
            p_nom_extendable=False)

solar_base = [0, 0, 0, 0, 0, 0, 0.1, 0.3, 0.6, 0.8, 0.9, 1.0, 0.95, 0.85, 0.6, 0.4, 0.15, 0.05, 0, 0, 0, 0, 0, 0]
solar_profile = solar_base * 365

network.add("Generator", "Mine Solar PV", bus="Mine Electricity Bus", 
            p_nom_extendable=True, 
            p_nom_max=30.0,         # Land constraint cap
            capital_cost=35000, 
            marginal_cost=5, 
            p_max_pu=solar_profile)

# 6. Add Conversion Links and Storage
network.add("Link", "Mine Diesel Generator Set", bus0="Mine Diesel Bus", bus1="Mine Electricity Bus", carrier="electricity", efficiency=0.35, p_nom_extendable=True, capital_cost=15000)

network.add("StorageUnit", "Mine Battery Storage", bus="Mine Electricity Bus", 
            p_nom_extendable=True, 
            p_nom_max=25.0,         # Converter speed ceiling limit
            capital_cost=55000, 
            max_hours=4, 
            efficiency_store=0.9, 
            efficiency_dispatch=0.9)

# 7. Run Optimization
print("\n--- Running Optimization via GLPK ---")
status = network.optimize(solver_name='glpk')
print(f"Optimization Status: {status}\n")

# 8. Setup Dataframe for Plotting
grid_dispatch = network.generators_t.p.loc[:, "Utility Grid"]
solar_dispatch = network.generators_t.p.loc[:, "Mine Solar PV"]

if "Mine Diesel Generator Set" in network.links_t.p1.columns:
    genset_dispatch = network.links_t.p1.loc[:, "Mine Diesel Generator Set"].abs()
else:
    genset_dispatch = pd.Series(0.0, index=snapshots)

raw_battery = network.storage_units_t.p.loc[:, "Mine Battery Storage"]
battery_discharge = raw_battery.clip(lower=0)
battery_charge = raw_battery.clip(upper=0)

dispatch_df = pd.DataFrame({
    "Utility Grid": grid_dispatch, 
    "Solar PV": solar_dispatch,
    "Diesel Generator": genset_dispatch,
    "Battery Discharging": battery_discharge,
    "Battery Charging": battery_charge
}, index=snapshots)

# 9. Generate and Display Plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the positive supply stack and negative charging region
dispatch_df.plot(kind="area", stacked=True, ax=ax, alpha=0.85, linewidth=0)

# Overlay the total demand line
network.loads_t.p["Electrical Load"].plot(color="black", linewidth=2.5, marker='o', ax=ax, label="Total Demand")

plt.title("Rectified Mine Microgrid Hourly Dispatch Schedule", fontsize=14, fontweight='bold')
plt.ylabel("Power (MW)", fontsize=12)
plt.xlabel("Time of Day", fontsize=12)

# Zoom into Jan 1st to Jan 4th window
ax.set_xlim(snapshots[0], snapshots[72])
# Set a clean layout bounds box
ax.set_ylim(dispatch_df["Battery Charging"].min() - 5, dispatch_df[["Utility Grid", "Solar PV", "Diesel Generator", "Battery Discharging"]].sum(axis=1).max() + 5)

plt.legend(loc="upper left", frameon=True)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

plt.savefig("mine_energy_dispatch.png", dpi=300)
print("Plot successfully saved as 'mine_energy_dispatch.png'")
plt.show()