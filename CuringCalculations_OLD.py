import math

PLANCK_CONSTANT = 6.62607004e-34  # Joules*second
SPEED_OF_LIGHT = 299792458  # meters/second
AVAGADROS_NUMBER = 6.02214076e23  # molecules/mole

# according to the DC2200, the forward voltage is 5.5V, the max current is 9.0A, and the wavelength is 445nm
voltage = 5.5
max_current = 9.0 # Amperes
wavelength = 445e-9  # nanometers -> meters
energy_required_to_crosslink = 1e-18  # Joules THIS WILL NEED TO CHANGE 
concentration_of_hyaluronic_acid = 15  # g/L
molecular_weight_of_hyaluronic_acid = 250e3  # kDa -> Da (g/mol)
molarity_of_hyaluronic_acid = concentration_of_hyaluronic_acid / molecular_weight_of_hyaluronic_acid  # M
molecules_per_meter_cubed = (molarity_of_hyaluronic_acid * AVAGADROS_NUMBER) / 1e-3  # molecules/m^3

energy_loss_ratio = 0.2  # This is a variable representing how much light actually reaches the gel. 0.0 is no light, 1.0 is all light. Energy that reaches gel / Total Energy emitted by lamp

current = 0.1  # Amperes, this can be changed by the user
target_stiffness = 10 # kPa, this can be changed by the user
beam_diameter = 0.045e-3  # millimeters -> meters
hyaluronic_acid_thickness = 1e-3  # millimeters -> meters

molecules_in_beam = molecules_per_meter_cubed * (math.pi * (beam_diameter/2)**2) * hyaluronic_acid_thickness  # molecules

wattage = voltage * current  # Watts

# photons per second calculations: https://socratic.org/questions/how-do-you-calculate-the-number-of-photons

# Good lumen definition: https://en.wikipedia.org/wiki/Lumen_(unit)

# 1 w = 75-110 lumens, according to https://www.voltlighting.com/learn/lumens-to-watts-conversion-led-bulb
# let's set this to 90 lumens per watt, because Thorlabs claims it is a "high-power LED"
# because this is subjective, we can change this later if needed
lumens = wattage * 90  # lumens

energy_per_photon = (PLANCK_CONSTANT * SPEED_OF_LIGHT) / wavelength  # Joules

total_energy_per_second = wattage * energy_loss_ratio  # Joules/second

photons_per_second = total_energy_per_second / energy_per_photon  # photons/second

energy_density = total_energy_per_second / (math.pi * (beam_diameter)**2)  # Joules/second/m^2

photon_density = photons_per_second / (math.pi * (beam_diameter)**2)  # photons/second/m^2

# This is a made up function. It is not based on any real data.
# It is just a function that takes in energy density and returns a relative stiffness index.
energy_density_to_stiffness_index = energy_density * 0.5  

photons_per_crosslink = energy_required_to_crosslink / energy_per_photon

crosslink_per_second = photons_per_second / photons_per_crosslink



def rate_of_crosslinking():
    # This will be a logarithmic function.
    # TODO: get molarity of HA gel and calculate molecules per meter cubed
    pass


def target_step_time(distance):
    pass
    
# print(crosslink_per_second)



     






# There are losses in the light path above the objective but these should be consistent across experiments as long as we don't 
# change any aspect of the path. So we can assume 'all' of the light from the lamp comes through the objective.  Things that 
# may vary are the lamp power, the motor speeds, and the height of the gel.  If we lower the gel we increase the diameter of the beam, 
# but the total number of photons hitting the illuminated circle is the same – a point receives the same number of photons while 
# traversing the beam diameter whether the diameter is 100 or 200 microns.  So we can express the light exposure of any point on a 
# gel as lamp power in milliwatts and the number of beam diameters (aka spot diameters) that point is exposed to during spot curing.
# Exposure = lamp power x speed (spot diameters/second) x seconds in the spot

# Examples
# Lanp 1000 mW, field diameter 200 microns, speed of the point 2 microns per second. Time within the spot is 10 s. 
# The point would need 100 seconds to traverse the spot, so in 10 s it covers 1/10th of spot diameter.  So it gets 100mW-diameters
# worth of photons. If it was in the beam for 100 seconds that equates to traveling one full diameter, that would be 1000 
# mW-diameters exposure. If the gel is lowered so the beam expands to 300 microns diameter, and the point of interest is still moving
#  at 2 microns per second, in 150 seconds it would get a full diameter, 1000 mW-diameters exposure, in 100 s 667 mW-diameters.

# Amendment
# I realized the first formulation doesn't account for a point that is stationary.
# we can use a point's speed (a function of the activity of the two motors) and the spot diameter to determine the time that 
# point spends within the illumination spot. dividing the lamp power by the spot area accounts for how the photons are more spread 
# when the gel is further below the objective and the spot is bigger, and more concentrated when the spot is smaller.
# the light exposure of any point is simply (lamp power/spot area)x(time in spot)
# please let me know your thoughts
# thanks



# Goal: Find time t (seconds) the light is in a spot  
# First, we need to map out the beam diameter for different stage heights. This will allow us to create a function of the beam diameter that can be extrapolated
# Second, we need to get data on the stiffness of the gel at different light exposures AND different stage heights. I wonder if changing light intensity and light duration will have different effects on the gel.
# Third, we will use the data from Step 2 to create a function that takes the light exposure (time and intensity) and returns the stiffness of the gel. This will be a logarithmic function based on the data collected from Step 2.
# Rejoice





# The beam diameter is a function of the stage height. We can use the following formula to calculate the beam diameter at any stage height:

focal_length = 3.7e-3  # meters according to https://bolioptics.com/40x-long-working-distance-plan-achromatic-metallurgical-microscope-objective-lens-working-distance-3-7mm/?gclid=Cj0KCQiA3eGfBhCeARIsACpJNU_o0--oh97gtA9GVT01KWzme-j-V3potb67rwwukO-mjUS3ExgTsRAaAiLbEALw_wcB
# Working distance is focal length (Also tested manually ~3.5mm)
objective_diameter = 1e-3  # mm -> meters. This is the smallest diameter of the beam before it reaches the objective. Becuase of the washer in the objective lens (1mm Diameter), this is set to 1mm
distance_from_lens = 9.7e-3  # mm -> meters. This is a test distance. The distance from focal point will be -6e-3
waist_radius = (2 * wavelength * focal_length) / (math.pi * objective_diameter)
rayleigh_range = (math.pi * waist_radius**2) / wavelength # https://www.rp-photonics.com/rayleigh_length.html
distance_from_focal_point = focal_length - distance_from_lens
beam_diameter = 2 * waist_radius * math.sqrt(1 + (distance_from_focal_point / rayleigh_range)**2) # meters

print(beam_diameter) 



# We can use the following formula to calculate the area of the beam at any stage height:
beam_area = math.pi * (beam_diameter / 2)**2


# We can use the following formula to calculate the time the light is in a spot:
# time_in_spot = beam_area / speed
# where beam_area is the area of the beam and speed is the speed of the point
# We can use the following formula to calculate the light exposure of any point:
# light_exposure = (lamp_power / beam_area) * time_in_spot
# where lamp_power is the power of the lamp
# We can use the following formula to calculate the stiffness of the gel:
# stiffness = f(light_exposure)
# where f is a function that takes light_exposure as input and returns the stiffness of the gel


