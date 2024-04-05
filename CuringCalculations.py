import math
import pandas as pd
from LensSimulator import Lens, Light

DEFAULT_CURRENT = 100 # mA
MAX_VELOCITY = 2.6 # mm/s
MIN_VELOCITY = 0.001 # mm/s
LIGHT_WAVELENGTH = 445 # nm
MIN_CURRENT = 0.1 # mA
MAX_CURRENT = 9000 # mA

class Configuration:
    current = None
    velocity = None
    iterations = 1

    def __repr__(self) -> str:
        return f"Configuration(current={self.current}, velocity={self.velocity}, iterations={self.iterations})"
    

    
class CuringCalculations:
    def __init__(self, target_stiffness, beam_diameter_mm):
        self.target_stiffness = target_stiffness
        self.beam_diameter = beam_diameter_mm

        df = pd.read_excel('Curing Calculations Data.xlsx')
        stiffness_to_photon_ratios = []
        for index, row in df.iterrows():
            beam_diameter = row['Beam Diameter (mm)']
            current = row['Current (mA)']
            velocity = row['Velocity (mm/s)']
            stiffness = row['Stiffness (kPa)']
            total_photon_exposure_per_pixel = self.get_total_photon_exposure_per_pixel(beam_diameter, current, velocity)
            stiffness_to_photon_ratios.append(stiffness / total_photon_exposure_per_pixel)

        self.average_ratio = sum(stiffness_to_photon_ratios) / len(stiffness_to_photon_ratios)


    def get_total_photon_exposure_per_pixel(self, beam_diameter, current, velocity):
        # made up number signifying that there are 100 photons in the light beam per second * current
        photon_constant = current * 100 # photons/s
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2
        photon_density = photon_constant / beam_area # photons/s/mm^2

        # how long a point is exposed as the light travels beam_diameter distance
        exposure_time_per_pixel = beam_diameter / velocity

        total_photon_exposure_per_pixel = photon_density * exposure_time_per_pixel # photons
        return total_photon_exposure_per_pixel

    def get_velocity_based_on_target_photon_exposure(self, beam_diameter, current, target_photon_exposure):
      # made up number signifying that there are 100 photons in the light beam per second * current
        photon_constant = current * 100 # photons/s
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2
        photon_density = photon_constant / beam_area # photons/s/mm^2

        target_velocity = (beam_diameter * photon_density) / target_photon_exposure
        return target_velocity 

    def get_current_based_on_target_photon_exposure(self, beam_diameter, velocity, target_photon_exposure):
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2

        exposure_time_per_pixel = beam_diameter / velocity
        target_current = (target_photon_exposure * beam_area) / (exposure_time_per_pixel * 100)
        return target_current

    def get_configuration(self):
        configuration = Configuration()
        unstable = True

        while unstable:
            # assuming linear relationship
            target_photon_exposure = self.target_stiffness / (self.average_ratio * configuration.iterations)
            new_velocity = self.get_velocity_based_on_target_photon_exposure(self.beam_diameter, DEFAULT_CURRENT, target_photon_exposure)
            if new_velocity < MIN_VELOCITY:
                new_velocity = MIN_VELOCITY
            elif new_velocity > MAX_VELOCITY:
                new_velocity = MAX_VELOCITY
            
            new_current = self.get_current_based_on_target_photon_exposure(self.beam_diameter, new_velocity, target_photon_exposure)

            if new_current < MIN_CURRENT:
                raise Exception("Unable to achieve target stiffness with current configuration, target stiffness and/or beam diameter is too low.")
            elif new_current > MAX_CURRENT:
                configuration.iterations += 1
                new_current = MAX_CURRENT
            else:
                unstable = False
            
            configuration.velocity = new_velocity
            configuration.current = new_current
        
        return configuration
    
curing_calculations = CuringCalculations(target_stiffness=0.1, beam_diameter_mm=1)
configuration = curing_calculations.get_configuration()
print(configuration)
