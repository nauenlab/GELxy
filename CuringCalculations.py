import math

PLANCK_CONSTANT = 6.62607004 * 10**-34  # Joules*second
SPEED_OF_LIGHT = 299792458  # meters/second

# according to the DC2200, the forward voltage is 5.5V, the max current is 9.0A, and the wavelength is 445nm
voltage = 5.5
max_current = 9.0 # Amperes
wavelength = 445  # nanometers
energy_loss_ratio = 0.2  # This is a variable representing how much light actually reaches the gel. 0.0 is no light, 1.0 is all light. Energy that reaches gel / Total Energy emitted by lamp


current = 0.1  # Amperes, this can be changed by the user
target_stiffness_index = 0.5  # This is a made up variable. It represents the relatve stiffness of the gel. 0.0 is very soft, 1.0 is very stiff
beam_diameter = 0.045  # millimeters

# 1 w = 75-110 lumens, according to https://www.voltlighting.com/learn/lumens-to-watts-conversion-led-bulb
def wattage(voltage, current):
    return voltage * current


# Good lumen definition: https://en.wikipedia.org/wiki/Lumen_(unit)

def lumens():
    # let's set this to 90 lumens per watt, because Thorlabs claims it is a "high-power LED"
    # because this is subjective, we can change this later if needed
    return wattage() * 90

def energy_per_photon():
    return (PLANCK_CONSTANT * SPEED_OF_LIGHT) / wavelength  # Joules

def photons_per_second():
    # This equation might be wrong. I saw this on StackOverflow, but I don't know if it is correct.
    return (((wattage() * wavelength) / PLANCK_CONSTANT) / SPEED_OF_LIGHT) * energy_loss_ratio # photons/second

def total_energy_per_second():
    return photons_per_second() * energy_per_photon() # Joules/second

def energy_density():
    # check this equation
    return total_energy_per_second() / (math.pi * (beam_diameter/1000)**2) # Joules/second/m^2


def energy_density_to_stiffness_index(energy_density):
    # This is a made up function. It is not based on any real data.
    # It is just a function that takes in energy density and returns a relative stiffness index.
    return energy_density * 0.5

def rate_of_crosslinking():
    # This will be a logarithmic function.
    # TODO: get molarity of HA gel and calculate molecules per meter cubed
    


def target_step_time(distance):

     

