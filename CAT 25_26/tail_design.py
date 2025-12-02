#%%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

csv_file = 'Selig.csv'  # Replace with your CSV filename

df = pd.read_csv(csv_file, delim_whitespace=True)

df.columns = df.columns.str.strip()

print(f"Columns found: {df.columns.tolist()}")
print(f"Number of data points: {len(df)}")
print(f"\nFirst few rows:")
print(df.head())

# Get x and y data
x_original = df['x'].values
y_original = df['y'].values

l = np.linspace(0.7, 1.3, 10)
# l = 1.00 #Moment arm, distance between cg and vertical aerodynamic center

#From Gustavo
c_w = 0.345 #Mean aerodynamic chord of main wing
b_w = 2.5 #Main wing span
S_w = c_w*b_w #Main wing refernce area

#From Snorri Gudmundsson
V_ht = 0.640
V_vt = 0.0383
#V_vt = (S_vt * l) / (S_w * b_w) #Volume for vertical tail
#V_ht = (S_ht * l) / (S_w * c_w) #Volume for horizontal tail

b_vertical_tail_list = []
c_horizontal_tail_list = []

def calculate_airfoil_area(x, y):
    # Integrate using trapezoidal rule
    area = np.trapz(y, x)
    return abs(area)

def scale_airfoil(x, y, chord_length):
    x_scaled = x * chord_length
    y_scaled = y * chord_length
    return x_scaled, y_scaled

for i in range(len(l)):
    
    S_vt = (V_vt * (S_w * b_w))/l[i] #Area of vt
    S_ht = (V_ht * (S_w * c_w))/l[i] #Area of ht
    print(f'\nArea of vertical tail: {S_vt:.3f} m^2')
    print(f'Area of horizontal tail: {S_ht:.3f} m^2')


    AR_horizontal_tail = 6

    b_horizontal_tail = np.sqrt(AR_horizontal_tail*S_ht) #span
    c_horizontal_tail = S_ht/b_horizontal_tail

    b_vertical_tail = S_vt/b_horizontal_tail

    print('Horizontal Tail wing')
    print(f'span = {b_horizontal_tail:.3f} m')
    print(f'chord = {c_horizontal_tail:.3f} m')

    print('Vertical Tail wing')
    print(f'span = {b_vertical_tail:.3f} m')
    
    b_vertical_tail_list.append(b_vertical_tail)
    c_horizontal_tail_list.append(c_horizontal_tail)
    
plt.figure()
plt.plot(l, b_vertical_tail_list)
plt.show()

chord_lengths = c_horizontal_tail_list

# Calculate areas for different chord lengths
results = []
for chord in chord_lengths:
    x_scaled, y_scaled = scale_airfoil(x_original, y_original, chord)
    area = calculate_airfoil_area(x_scaled, y_scaled)
    results.append({'Chord Length': chord, 'Area': area})
    print(f"Chord Length: {chord:.2f} m, Area: {area:.6f} m²")

# Create results dataframe
results_df = pd.DataFrame(results)

plt.figure()
for chord in chord_lengths:
    x_scaled, y_scaled = scale_airfoil(x_original, y_original, chord)
    plt.plot(x_scaled, y_scaled, label=f'c = {chord:.2f} m', alpha=0.7)
plt.xlabel('x (m)')
plt.ylabel('x (m)')
plt.title('Airfoil Profiles at Different Chord Lengths')
plt.axis('equal')
plt.tight_layout()
plt.legend()
plt.savefig('Airfoil Profiles at Different Chord Lengths.png', dpi=300, bbox_inches='tight')
plt.show()

plt.figure()
plt.plot(results_df['Chord Length'], results_df['Area'], 'o-', linewidth=2, markersize=8)
plt.xlabel('Chord Length (m)')
plt.ylabel('Area (m²)')
plt.title('Airfoil Area vs Chord Length')
plt.tight_layout()
plt.legend()
plt.savefig('Airfoil Area vs Chord Length.png', dpi=300, bbox_inches='tight')
plt.show()
#%%