import math
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# ===============================
# Constants
# ===============================
g = 9.81  # m/s²
R = 287.05  # gas constant for dry air (J/kg·K)
OMEGA = 7.2921159e-5  # Earth's rotation rate (rad/s)

FUEL_DATABASE = {
    "butane": 111.0,   # MJ/m³
    "propane": 94.0,
    "hairspray": 60.0
}

# ===============================
# Utility: Volume of a cylinder
# ===============================
def cylinder_volume(length_m, diameter_m):
    radius = diameter_m / 2
    return math.pi * radius**2 * length_m

# ===============================
# Atmospheric model
# ===============================
def air_density(altitude_m, temperature_c):
    T = temperature_c + 273.15
    p0 = 101325
    p = p0 * (1 - 2.25577e-5 * altitude_m) ** 5.25588
    return p / (R * T)  # kg/m³

# ===============================
# Muzzle velocity estimation
# ===============================
def estimate_muzzle_velocity(barrel_len, barrel_dia, chamber_len, chamber_dia, projectile_mass, fuel_type, fuel_ml):
    barrel_vol = cylinder_volume(barrel_len, barrel_dia)
    chamber_vol = cylinder_volume(chamber_len, chamber_dia)
    
    fuel_m3 = fuel_ml / 1_000_000
    energy_density = FUEL_DATABASE.get(fuel_type.lower(), 90) * 1_000_000
    chemical_energy = fuel_m3 * energy_density
    kinetic_energy = chemical_energy * 0.15  # 15% efficiency
    
    muzzle_velocity = math.sqrt(2 * kinetic_energy / projectile_mass)
    return muzzle_velocity, barrel_vol, chamber_vol

# ===============================
# Drag + Coriolis simulation
# ===============================
def simulate_range_with_drag_coriolis(angle_deg, v0, h, mass, cd, area, rho, wind_speed=0, lat_deg=0, azimuth_deg=90):
    dt = 0.01
    theta = math.radians(angle_deg)
    azimuth = math.radians(azimuth_deg)
    lat = math.radians(lat_deg)

    # Velocity components in local ENU (East, North, Up)
    vx = v0 * math.cos(theta) * math.cos(azimuth) + wind_speed
    vy = v0 * math.cos(theta) * math.sin(azimuth)
    vz = v0 * math.sin(theta)

    x, y, z = 0.0, 0.0, h
    t = 0.0

    while z > 0:
        v = math.sqrt(vx**2 + vy**2 + vz**2)
        drag = 0.5 * rho * cd * area * v**2 / mass

        # Coriolis acceleration components
        ax_coriolis =  2 * OMEGA * (vy * math.sin(lat) - vz * math.cos(lat) * math.sin(azimuth))
        ay_coriolis = -2 * OMEGA * (vx * math.sin(lat))
        az_coriolis =  2 * OMEGA * (vx * math.cos(lat) * math.sin(azimuth))

        # Apply accelerations
        ax = - (drag * vx / v) + ax_coriolis
        ay = - (drag * vy / v) + ay_coriolis
        az = -g - (drag * vz / v) + az_coriolis

        # Update velocities
        vx += ax * dt
        vy += ay * dt
        vz += az * dt

        # Update positions
        x += vx * dt
        y += vy * dt
        z += vz * dt
        t += dt

    horizontal_range = math.sqrt(x**2 + y**2)
    impact_speed = math.sqrt(vx**2 + vy**2 + vz**2)
    drift = y  # Lateral deflection
    return horizontal_range, t, impact_speed, drift

# ===============================
# Firing table generator
# ===============================
def generate_firing_table(v0, h, mass, cd, area, rho, wind_speed, lat, azimuth):
    print("\n=== Firing Table (with Coriolis) ===")
    print("Angle | Range (m) | Time (s) | Impact Vel (m/s) | Drift (m)")
    print("------------------------------------------------------------")
    for angle in range(15, 76, 5):
        rng, tof, imp_v, drift = simulate_range_with_drag_coriolis(angle, v0, h, mass, cd, area, rho, wind_speed, lat, azimuth)
        print(f"{angle:>3}°  | {rng:>8.1f} | {tof:>7.2f} | {imp_v:>8.2f} | {drift:>7.2f}")

# ===============================
# Graph mode
# ===============================
def plot_graph(v0, h, mass, cd, area, rho, wind_speed, lat, azimuth):
    angles = np.linspace(10, 80, 50)
    ranges = []
    for a in angles:
        r, _, _, _ = simulate_range_with_drag_coriolis(a, v0, h, mass, cd, area, rho, wind_speed, lat, azimuth)
        ranges.append(r)
    
    plt.figure(figsize=(10, 6))
    plt.plot(angles, ranges, label="With Drag + Coriolis")
    plt.xlabel("Launch Angle (degrees)")
    plt.ylabel("Range (m)")
    plt.title("Potato Cannon Trajectory (Drag + Coriolis)")
    plt.grid(True)
    plt.legend()
    plt.show()

# ===============================
# Save/load cannon profiles
# ===============================
def save_profile(profile, filename="cannon_profiles.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[profile["name"]] = profile
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Profile '{profile['name']}' saved.")

def load_profile(name, filename="cannon_profiles.json"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        return data.get(name)
    return None

# ===============================
# Main interactive program
# ===============================
def main():
    print("\n=== Potato Cannon Simulator v3 ===")
    choice = input("Load existing profile? (y/n): ").lower()
    
    if choice == "y":
        name = input("Enter profile name: ")
        profile = load_profile(name)
        if not profile:
            print("Profile not found.")
            return
    else:
        profile = {}
        profile["name"] = input("Enter cannon name: ")
        profile["barrel_len"] = float(input("Barrel length (m): "))
        profile["barrel_dia"] = float(input("Barrel diameter (m): "))
        profile["chamber_len"] = float(input("Chamber length (m): "))
        profile["chamber_dia"] = float(input("Chamber diameter (m): "))
        profile["proj_mass"] = float(input("Projectile mass (kg): "))
        profile["fuel_type"] = input("Fuel type (butane/propane/hairspray): ")
        profile["fuel_ml"] = float(input("Fuel amount (ml): "))
        profile["launch_height"] = float(input("Launch height (m): "))
        profile["cd"] = 0.47  # Sphere-like
        profile["altitude"] = float(input("Altitude (m): "))
        profile["temp"] = float(input("Temperature (°C): "))
        profile["latitude"] = float(input("Latitude (°): "))
        profile["azimuth"] = float(input("Azimuth (°) [0=N, 90=E, 180=S, 270=W]: "))
        save_profile(profile)

    # Air density
    rho = air_density(profile["altitude"], profile["temp"])
    
    # Cross-sectional area
    area = math.pi * (profile["barrel_dia"] / 2)**2
    
    # Estimate muzzle velocity
    v0, barrel_vol, chamber_vol = estimate_muzzle_velocity(
        profile["barrel_len"], profile["barrel_dia"],
        profile["chamber_len"], profile["chamber_dia"],
        profile["proj_mass"], profile["fuel_type"], profile["fuel_ml"]
    )

    print(f"\nEstimated muzzle velocity: {v0:.2f} m/s")
    print(f"Air density: {rho:.3f} kg/m³")
    print(f"Barrel volume: {barrel_vol*1000:.2f} L")
    print(f"Chamber volume: {chamber_vol*1000:.2f} L")
    print(f"Chamber-to-barrel ratio: {chamber_vol/barrel_vol:.2f}:1")

    while True:
        print("\n1. Generate firing table")
        print("2. Plot range vs. angle graph")
        print("3. Predict for custom angle")
        print("4. Exit")
        mode = input("Choose option: ")

        if mode == "1":
            ws = float(input("Wind speed (km/h, tailwind positive): "))
            generate_firing_table(v0, profile["launch_height"], profile["proj_mass"], profile["cd"], area, rho, ws/3.6, profile["latitude"], profile["azimuth"])

        elif mode == "2":
            ws = float(input("Wind speed (km/h, tailwind positive): "))
            plot_graph(v0, profile["launch_height"], profile["proj_mass"], profile["cd"], area, rho, ws/3.6, profile["latitude"], profile["azimuth"])

        elif mode == "3":
            ang = float(input("Launch angle (°): "))
            ws = float(input("Wind speed (km/h, tailwind positive): "))
            rng, tof, imp_v, drift = simulate_range_with_drag_coriolis(ang, v0, profile["launch_height"], profile["proj_mass"], profile["cd"], area, rho, ws/3.6, profile["latitude"], profile["azimuth"])
            print(f"Range: {rng:.2f} m | Time: {tof:.2f} s | Impact velocity: {imp_v:.2f} m/s | Drift: {drift:.2f} m")

        elif mode == "4":
            print("Exiting.")
            break

if __name__ == "__main__":
    main()
