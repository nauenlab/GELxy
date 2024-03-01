import math
import enum
import pandas as pd

class ObjectStep:
    def __init__(self, distance_from_light):
        self.distance_from_light = distance_from_light

class Lens(ObjectStep):
    def __init__(self, focal_length, lens_input_diameter, distance_from_light, lens_thickness):
        super().__init__(distance_from_light)
        self.focal_length = focal_length
        self.lens_input_diameter = lens_input_diameter
        self.lens_thickness = lens_thickness

    def get_projected_diameter(self, wavelength, distance_from_lens, light_input_diameter):
        waist_radius = (2 * wavelength * self.focal_length) / (math.pi * min(self.lens_input_diameter, light_input_diameter))
        rayleigh_range = (math.pi * waist_radius**2) / wavelength # https://www.rp-photonics.com/rayleigh_length.html
        distance_from_focal_point = self.focal_length - distance_from_lens
        projected_diameter = 2 * waist_radius * math.sqrt(1 + (distance_from_focal_point / rayleigh_range)**2) # meters
        
        return projected_diameter

class Light:
    def __init__(self, wavelength, diameter):
        self.wavelength = wavelength
        self.diameter = diameter

class Gel:
    def __init__(self, distance_from_light):
        self.distance_from_light = distance_from_light

class Pinhole(ObjectStep):
    def __init__(self, diameter, distance_from_light):
        super().__init__(distance_from_light)
        self.diameter = diameter


class LensSimulator:
    def __init__(self, objects, light, gel):
        self.objects = objects
        self.light = light
        self.gel = gel
    
    def get_output_diameter(self):
        light_input_diameter = self.light.diameter
        prev_object = None
        for object in self.objects:
            if object is Pinhole:
                light_input_diameter = object.diameter
                continue

            if prev_object:
                light_input_diameter = prev_object.get_projected_diameter(self.light.wavelength, object.distance_from_light - prev_object.distance_from_light + prev_object.lens_thickness, light_input_diameter)

            prev_object = object

        if prev_object is Lens:
            output_diameter = prev_object.get_projected_diameter(self.light.wavelength, self.gel.distance_from_light - prev_object.distance_from_light + prev_object.lens_thickness, light_input_diameter)
        
            return output_diameter

        raise Exception('The last object must be a lens')





# Thorlabs Lenses are often made of N-BK7, whose refractive index can be found here:
# https://www.filmetrics.com/refractive-index-database/Schott+N-BK7#:~:text=For%20a%20typical%20sample%20of,refractive%20index%20and%20extinction%20coefficients.
# The refractive index of N-BK7 is 1.52579 at a wavelength of 445 nm
# The focal length of the lens is 300mm ± 3mm


class ThorLabsLens:
    class Material(enum.Enum):
        nkb7 = "N-BK7_refractive_index.txt"
    
        def refractive_index(self, wavelength):
            if self == ThorLabsLens.Material.nkb7:
                df = pd.read_csv(self.value, delimiter='\t')
                return df.loc[df['Wavelength(nm)'] == wavelength, 'n'].values[0]
            

    def __init__(self, focal_length, design_wavelength, material):
        # Make sure to round the wavelength to the nearest 5nm
        self.focal_length = focal_length
        self.design_wavelength = design_wavelength
        self.material = material

    def get_focal_length_at_wavelength(self, target_wavelength):
        # Make sure to round the wavelength to the nearest 5nm
        r = 1 / ((self.material.refractive_index(self.design_wavelength) - 1) * self.focal_length)
        focal_length_at_wavelength = 1 / ((self.material.refractive_index(target_wavelength) - 1) * r)

        return focal_length_at_wavelength


print(ThorLabsLens(300, 635, ThorLabsLens.Material.nkb7).get_focal_length_at_wavelength(445))








lens1 = Lens(focal_length=3.7e-3, lens_input_diameter=1e-3, distance_from_light=9.7e-3, lens_thickness=1e-3)
