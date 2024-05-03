import math
import pandas as pd

DEFAULT_CURRENT = 100 # mA
MAX_VELOCITY = 2.6 # mm/s
MIN_VELOCITY = 0.005 # mm/s
LIGHT_WAVELENGTH = 445 # nm
MIN_CURRENT = 0.1 # mA
MAX_CURRENT = 9000 # mA


class Configuration:
    """
    Represents the configuration for curing calculations.
    """
    current = None
    velocity = None
    iterations = 1

    def __repr__(self) -> str:
        return f"Configuration(current={self.current}, velocity={self.velocity}, iterations={self.iterations})"
    
    
class CuringCalculations:
    """
    Performs curing calculations based on given parameters.
    """
    def __init__(self):
        """
        Initializes the CuringCalculations object and reads the curing calculations data from an Excel file.
        """
        df = pd.read_excel('Curing Calculations Data.xlsx')
        stiffness_to_photon_ratios = []
        for index, row in df.iterrows():
            beam_diameter = row['Beam Diameter (mm)']
            current = row['Current (mA)']
            velocity = row['Velocity (mm/s)']
            stiffness = row['Stiffness (kPa)']
            total_photon_exposure_per_pixel = self.get_total_photon_exposure_per_pixel(beam_diameter, current, velocity)
            stiffness_to_photon_ratios.append(self.calculate_stiffness_to_photon_ratio(stiffness, total_photon_exposure_per_pixel))

        self.average_ratio = sum(stiffness_to_photon_ratios) / len(stiffness_to_photon_ratios)

    def calculate_stiffness_to_photon_ratio(self, stiffness, photon_exposure):
        """
        Calculates the stiffness-to-photon ratio based on the given stiffness and photon exposure.

        Args:
            stiffness (float): The stiffness value in kPa.
            photon_exposure (float): The total photon exposure in photons.

        Returns:
            float: The stiffness-to-photon ratio.
        """
        # This will need to change as we get more data
        # This is assuming a linear relationship between stiffness and photon exposure. In reality, it is likely more logarithmic.
        return stiffness / photon_exposure

    def get_total_photon_exposure_per_pixel(self, beam_diameter, current, velocity):
        """
        Calculates the total photon exposure per pixel based on the given beam diameter, current, and velocity.

        Args:
            beam_diameter (float): The beam diameter in mm.
            current (float): The current value in mA.
            velocity (float): The velocity value in mm/s.

        Returns:
            float: The total photon exposure per pixel in photons.
        """
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2
        photon_density = current / beam_area # photons/s/mm^2

        # how long a point is exposed as the light travels beam_diameter distance
        # TODO: This variable is considering the light beam through the largest part of the circle (diameter). It does not consider smaller light paths.
        exposure_time_per_pixel = beam_diameter / velocity
        
        total_photon_exposure_per_pixel = photon_density * exposure_time_per_pixel # photons
        return total_photon_exposure_per_pixel

    def get_velocity_based_on_target_photon_exposure(self, beam_diameter, current, target_photon_exposure):
        """
        Calculates the velocity based on the target photon exposure, beam diameter, and current.

        Args:
            beam_diameter (float): The beam diameter in mm.
            current (float): The current value in mA.
            target_photon_exposure (float): The target photon exposure in photons.

        Returns:
            float: The velocity value in mm/s.
        """
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2
        photon_density = current / beam_area # photons/s/mm^2

        target_velocity = (beam_diameter * photon_density) / target_photon_exposure
        return target_velocity 

    def get_current_based_on_target_photon_exposure(self, beam_diameter, velocity, target_photon_exposure):
        """
        Calculates the current based on the target photon exposure, beam diameter, and velocity.

        Args:
            beam_diameter (float): The beam diameter in mm.
            velocity (float): The velocity value in mm/s.
            target_photon_exposure (float): The target photon exposure in photons.

        Returns:
            float: The current value in mA.
        """
        beam_area = math.pi * (beam_diameter / 2)**2 # mm^2

        exposure_time_per_pixel = beam_diameter / velocity
        target_current = (target_photon_exposure * beam_area) / exposure_time_per_pixel
        return target_current

    def get_configuration(self, target_stiffness, beam_diameter_mm):
        """
        Calculates the configuration based on the target stiffness and beam diameter.

        Args:
            target_stiffness (float): The target stiffness value in kPa.
            beam_diameter_mm (float): The beam diameter in mm.

        Returns:
            Configuration: The calculated configuration.
        
        Raises:
            Exception: If unable to achieve the target stiffness with the current configuration.
        """
        configuration = Configuration()
        target_exposure = self.calculate_stiffness_to_photon_ratio(target_stiffness, self.average_ratio)

        while True:
            velocity = self.get_velocity_based_on_target_photon_exposure(beam_diameter_mm, DEFAULT_CURRENT, target_exposure / configuration.iterations)
            velocity = max(MIN_VELOCITY, min(velocity, MAX_VELOCITY))
            
            current = self.get_current_based_on_target_photon_exposure(beam_diameter_mm, velocity, target_exposure / configuration.iterations)
            if current < MIN_CURRENT:
                raise Exception("Configuration not achievable with current parameters.")
            
            if current > MAX_CURRENT:
                configuration.iterations += 1
                continue
            
            configuration.velocity = velocity
            configuration.current = current
            break

        return configuration
    

curing_calculations = CuringCalculations()
configuration1 = curing_calculations.get_configuration(target_stiffness=0.1, beam_diameter_mm=3)
