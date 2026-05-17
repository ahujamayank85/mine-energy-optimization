Project Title: Mine Energy System Optimisation

Objective: Optimization of mine enregy systems based on their availability, cost, etc.

Methodology: Python 3.10, PyPSA and GLPK Solver were used during the development.

Key Findings: For shorter time duration, the solver suggested that installation cost of solar cost was not required and energy requirement duing peak hours could be met through diesel. However, increasing the time horizon resulted in utilization of only solar energy and battery storage since there was no cap on the installation capacity of solar and battery storage. Capping solar at 30 MW forced the network to re-engage grid utility power during peak hours to avoid deficits and resulted in graph shown as "mine_energy_dispatch.png" curve. 
