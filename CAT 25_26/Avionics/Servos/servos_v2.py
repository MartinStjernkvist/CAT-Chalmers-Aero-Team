#%%
import numpy as np
import matplotlib.pyplot as plt

SMALL_SIZE = 10
MEDIUM_SIZE = 12
BIGGER_SIZE = 14
dpi = 500

plt.rc('font', size=SMALL_SIZE)
plt.rc('axes', titlesize=BIGGER_SIZE)
plt.rc('axes', labelsize=MEDIUM_SIZE)
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('legend', fontsize=SMALL_SIZE)
plt.rc('figure', titlesize=BIGGER_SIZE)
plt.rc('figure', figsize=(8,4))

RHO = 1.2 # Air Density (kg/m^3)
NM_TO_KGCM = 10.2

def calculate_servo_torque(alpha_servo_deg, alpha_control_deg, params, use_dynamic_cd=False):

    # Convert angles to radians
    ah = np.deg2rad(alpha_control_deg)
    as_ = np.deg2rad(alpha_servo_deg)
    
    # Drag coefficient (Cd)
    if use_dynamic_cd:
        # Appendix: "Cd is 1.28 times the sine of the inclination angle"
        # This results in much lower torque at small angles.
        cd = 1.28 * np.sin(ah)
    else:
        # Author's conservative recommendation
        cd = 1.0

    # Formula Eq(9): Ts = Cd * rho * V^2 * L * C^2 * sin(ah) * tan(ah) / (4 * tan(as))
    term1 = cd * RHO * params['V']**2 * params['L'] * params['C']**2
    numerator = term1 * np.sin(ah) * np.tan(ah)
    denominator = 4 * np.tan(as_)
    
    torque_nm = numerator / denominator
    
    return torque_nm * NM_TO_KGCM

def plot_torque_requirements(servo_angles, control_deflections):

    plt.figure()
    
    for deflection in control_deflections:
        # Conservative Calculation (Cd=1.0)
        torques_conservative = calculate_servo_torque(servo_angles, deflection, params, use_dynamic_cd=False)
        
        plt.plot(servo_angles, torques_conservative, linestyle='--', 
                 label=f'Deflection {deflection}° (Conservative Cd=1.0)')
        
        # Dynamic calculation (Cd varies) - Optional, for comparison
        torques_dynamic = calculate_servo_torque(servo_angles, deflection, params, use_dynamic_cd=True)
        
        plt.plot(servo_angles, torques_dynamic, linestyle='-', linewidth=2, 
                 label=f'Deflection {deflection}° (Dynamic Cd)')

    plt.title(f"Servo Torque Required \n(V={params['V']} m/s, L={params['L']}m, C={params['C']}m)")
    plt.xlabel("Servo arm angle (degrees)")
    plt.ylabel("Torque required (kg-cm)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # Case: 45 deg deflection, 45 deg servo, Cd=1.0
    # check_val = calculate_servo_torque(45, 45, params, use_dynamic_cd=False)
    # print(f"VERIFICATION: At 45 deg deflection & 45 deg servo angle (Cd=1.0): {check_val:.2f} kg-cm")

def calculate_torque(alpha_servo, alpha_surface):

    ah = np.deg2rad(alpha_surface)
    as_ = np.deg2rad(alpha_servo)
    cd = 1.28 * np.sin(ah) # Dynamic Drag Coefficient
    
    # Torque Formula
    T_nm = (cd * RHO * params['V']**2 * params['L'] * params['C']**2 * np.sin(ah) * np.tan(ah)) / (4 * np.tan(as_))
    return T_nm * NM_TO_KGCM

def plot_torque_multiplier_verification():
    """
    Recreates the graph from Page 3 of the PDF  to verify accuracy.
    """
    # PDF analyzes a 45 degree control surface deflection 
    control_deflection = 45 
    
    # Servo angles to test (10 to 60) [cite: 64-70]
    test_angles = np.array([60, 50, 40, 30, 20, 10])
    
    torques = calculate_servo_torque(test_angles, control_deflection, params)
    
    # Normalize relative to 60 degrees (where multiplier = 1.0) [cite: 54]
    base_torque = torques[0] # Torque at 60 degrees
    multipliers = torques / base_torque
    
    plt.figure()
    plt.plot(test_angles, multipliers, 's-', linewidth=2, color='navy')
    
    # Match the PDF graph formatting 
    plt.gca().invert_xaxis() # PDF graph goes 60 -> 10
    plt.title("Verification: Torque Multiplier (Matches PDF Page 3)")
    plt.xlabel("Servo Arm Rotation Angle (degrees)")
    plt.ylabel("Torque Multiplier (Relative to 60°)")
    plt.grid(True, which='both', linestyle='--')
    
    # Annotate specific points mentioned in text
    plt.annotate('Multiplier ~2x at 40° [cite: 52]', xy=(40, multipliers[2]), 
                 xytext=(40, 4), arrowprops=dict(arrowstyle='->'))
    plt.annotate('Multiplier ~10x at 10° ', xy=(10, multipliers[5]), 
                 xytext=(20, 8), arrowprops=dict(arrowstyle='->'))

    plt.tight_layout()
    print("Generated Torque Multiplier Verification Plot")
    plt.show()
    
def visualize_servo_geometry():

    setups = [
        {'servo_angle': 60, 'title': 'Efficient setup (High servo travel)'},
        {'servo_angle': 20, 'title': 'Inefficient setup (Low servo travel)'}
    ]
    
    surface_angle = 45 # Fixed target deflection
    horn_length = 2.0 # cm (Reference length)
    
    fig, axes = plt.subplots(2, 1, figsize=(8, 8))
    
    for ax, setup in zip(axes, setups):
        s_angle = setup['servo_angle']
        
        # Calculate required servo arm length to achieve surface_angle
        # using the approximation: L_servo * sin(s_angle) = L_horn * sin(surface_angle)
        servo_arm_len = horn_length * np.sin(np.deg2rad(surface_angle)) / np.sin(np.deg2rad(s_angle))
        
        torque = calculate_torque(s_angle, surface_angle)
        
        # Draw servo pivot and arm
        ax.plot(0, 0, 'ko', markersize=8, label='Servo Pivot')
        
        # Servo arm neutral
        ax.plot([0, 0], [0, servo_arm_len], 'k--', alpha=0.3)
        
        # Servo arm deflected
        sx = -servo_arm_len * np.sin(np.deg2rad(s_angle))
        sy = servo_arm_len * np.cos(np.deg2rad(s_angle))
        ax.plot([0, sx], [0, sy], 'b-', linewidth=4, label='Servo Arm')
        
        # Draw horn pivot (Offset distance) and horn
        pivot_dist = 5.0 # Arbitrary distance for visualization
        ax.plot(pivot_dist, 0, 'ks', markersize=8, label='Surface Hinge')
        
        # Horn Neutral (Dashed)
        ax.plot([pivot_dist, pivot_dist], [0, horn_length], 'k--', alpha=0.3)
        
        # Horn Deflected (Solid Green)
        hx = pivot_dist - horn_length * np.sin(np.deg2rad(surface_angle))
        hy = horn_length * np.cos(np.deg2rad(surface_angle))
        ax.plot([pivot_dist, hx], [0, hy], 'g-', linewidth=4, label='Control Horn')
        
        # Connecting pushrod
        ax.plot([sx, hx], [sy, hy], 'r-', linewidth=1.5, label='Pushrod')
        
        ax.set_title(f"{setup['title']}\nServo rotates {s_angle}° to move Surface {surface_angle}°")
        ax.set_aspect('equal')
        ax.set_xlim(-3, 7)
        ax.set_ylim(-1, max(servo_arm_len, horn_length) + 1)
        ax.legend(loc='lower right')
        
        info = (f"Servo Arm: {servo_arm_len:.1f} cm\n"
                f"Horn Length: {horn_length} cm\n"
                f"Torque Reqd: {torque:.1f} kg-cm")
        
        ax.text(0.05, 0.95, info, transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle="round", fc="w", alpha=0.9))

    plt.tight_layout()
    plt.show()
    
def plot_linearised_torque(s_min, s_max, c_min, c_max, params):
    s_angles = np.linspace(s_min, s_max, 100)
    
    # Calculate the linearly mapped control surface angles
    slope = (c_max - c_min) / (s_max - s_min)
    c_angles = c_min + slope * (s_angles - s_min)
    
    # Calculate torques using the existing vectorized function
    torques_conservative = calculate_servo_torque(s_angles, c_angles, params, use_dynamic_cd=False)
    torques_dynamic = calculate_servo_torque(s_angles, c_angles, params, use_dynamic_cd=True)
    
    plt.figure()
    
    # We plot against the Control Surface Deflection for intuition, 
    # but you could easily swap 'c_angles' for 's_angles' if you prefer tracking the servo.
    plt.plot(c_angles, torques_conservative, linestyle='--', color='red',
             label='Conservative (Cd=1.0)')
    plt.plot(c_angles, torques_dynamic, linestyle='-', linewidth=2, color='blue',
             label='Dynamic Cd')
    
    plt.title(f"Operational Torque Curve\nServo: {s_min}° to {s_max}°, Surface: {c_min}° to {c_max}°")
    plt.xlabel("Control Surface Deflection (degrees)")
    plt.ylabel("Torque required (kg-cm)")
    
    # Adding a secondary X-axis to show the corresponding Servo Angle
    ax1 = plt.gca()
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    
    # Set the ticks for the top axis to match the servo angles
    tick_locs = ax1.get_xticks()

    valid_ticks = [t for t in tick_locs if c_min <= t <= c_max]
    mapped_servo_ticks = [s_min + (t - c_min) / slope for t in valid_ticks]
    
    ax2.set_xticks(valid_ticks)
    ax2.set_xticklabels([f"{st:.1f}°" for st in mapped_servo_ticks])
    ax2.set_xlabel("Corresponding Servo Angle")

    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')
    plt.tight_layout()
    plt.show()
    
def plot_kinematic_torque(s_max, c_max, params):
    
    s_angles = np.linspace(1, s_max, 100)
    
    # Calculate the mechanical linkage ratio (Rs/Rc) required to achieve the max throws
    K = np.sin(np.deg2rad(c_max)) / np.sin(np.deg2rad(s_max))
    
    # Calculate true non-linear control surface angles
    c_angles_rad = np.arcsin(K * np.sin(np.deg2rad(s_angles)))
    c_angles = np.rad2deg(c_angles_rad)
    
    # Calculate torques using the existing vectorized function
    torques_conservative = calculate_servo_torque(s_angles, c_angles, params, use_dynamic_cd=False)
    torques_dynamic = calculate_servo_torque(s_angles, c_angles, params, use_dynamic_cd=True)
    
    fig, ax1 = plt.subplots()
    
    ax1.plot(s_angles, torques_conservative, linestyle='--', color='red',
             label='Torque (Conservative Cd=1.0)')
    ax1.plot(s_angles, torques_dynamic, linestyle='-', linewidth=2, color='blue',
             label='Torque (Dynamic Cd)')
    
    ax1.set_title(f"True Kinematic Torque Curve\nMax Servo: {s_max}°, Max Surface: {c_max}°")
    ax1.set_xlabel("Servo Angle (degrees)")
    ax1.set_ylabel("Torque required (kg-cm)")
    
    # Secondary Y-axis to visualize the non-linear angle mapping
    ax2 = ax1.twinx()
    ax2.plot(s_angles, c_angles, 'k:', linewidth=2, alpha=0.6, label='Control Surface Angle')
    ax2.set_ylabel("True Control Surface Deflection (°)", color='k', alpha=0.8)
    ax2.tick_params(axis='y', labelcolor='k')
    
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    
    ax1.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    
#%%
####################################################################################################
# Plane parameters
####################################################################################################

# IMPORTANT
# There's a correct and wrong way to read the data.
# Do not just look at maximum value.
# We want max deflection of control surface at max deflection of servo.

params = {
    'L': 2 * 0.464, # Control surface length (meters)
    'C': 0.0534, # Control surface chord (meters)
    'V': 30, # Airspeed (m/s)
}

s_min = 1
s_max = 50
c_min = 1
c_max = 40

servo_angles = np.linspace(s_min, s_max, 100)
control_deflections = np.linspace(c_min, c_max, 5)

plot_torque_requirements(servo_angles, control_deflections)
plot_linearised_torque(s_min, s_max, c_min, c_max, params=params)
plot_kinematic_torque(s_max, c_max, params=params)

# plot_torque_multiplier_verification()
# visualize_servo_geometry()
#%%