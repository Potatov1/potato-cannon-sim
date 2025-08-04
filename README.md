
=========================================================
PROJECT: PCS-V3  (POTATO CANNON SIMULATOR - VERSION 3)
CLASSIFICATION: UNRESTRICTED / EDUCATIONAL USE
=========================================================

DESCRIPTION:
PCS-V3 is a physics-based projectile modeling and fire-control simulator
for experimental launchers. Designed for potato cannons, spud guns, and
other low-energy ballistic systems, PCS-V3 applies real-world artillery
principles to hobbyist-scale launchers.

SYSTEM CAPABILITIES:
- Calculates projectile trajectory with atmospheric and drag effects
- Compensates for wind speed and direction
- Models Coriolis drift based on geographic latitude and azimuth
- Estimates muzzle velocity from launcher dimensions and fuel input
- Generates firing tables for multiple elevation angles
- Produces trajectory plots for visual analysis
- Saves and recalls launcher configurations via profile system

TECHNICAL PARAMETERS:
- Supported fuels: Butane, Propane, Hairspray (user defined)
- Barrel and chamber dimensions: User configurable
- Projectile mass range: 0.01 kg - 5.0 kg
- Launch elevation: User defined (m above ground level)
- Operating altitude: Sea level to 5000 m
- Latitude support: -90° to +90°

SYSTEM REQUIREMENTS:
- Python 3.8 or higher
- NumPy, Matplotlib libraries

OPERATIONAL USAGE:
1. Create or load a launcher profile
2. Input environmental conditions
3. Generate firing tables and/or plot trajectories
4. Adjust angle and fuel for desired range

NOTES:
- PCS-V3 is intended for educational demonstration of ballistics modeling.
- Not certified for military or law enforcement operational use.
- Operator assumes all responsibility for safe launcher operation.

AUTHOR: [potatove]
VERSION: 3.0
DATE: [August 4th 2025]
=========================================================
