import math
import pandas as pd


def get_total_photons_exposure_per_pixel(beam_diameter, velocity):
    # just a really small pixel square
    pixel = 0.000001 # mm^2
    # made up number signifying that there are 100 photons in the light beam per second
    photon_constant = 100 # photons/s

    beam_diameter = 3 # mm
    beam_area = math.pi * (beam_diameter / 2)**2 # mm^2

    photon_density = photon_constant / beam_area # photons/s/mm^2

    # how long a point is exposed as the light travels beam_diameter distance
    exposure_time_per_pixel = beam_diameter / velocity 

    total_photons_exposure_per_pixel = photon_density * exposure_time_per_pixel * pixel # photons
    return total_photons_exposure_per_pixel




def main():

    df = pd.read_excel('Curing Calculations Data.xlsx')
    for index, row in df.iterrows():
        beam_diameter = row['Beam Diameter (mm)']
        current = row['Current (mA)']
        velocity = row['Velocity (mm/s)']
        stiffness = row['Stiffness (kPa)']
        total_photons_exposure_per_pixel = get_total_photons_exposure_per_pixel(beam_diameter, velocity)
        print(total_photons_exposure_per_pixel)

    # target_stiffness = 0.5 # Pa
    # # if linear relationship
    # # target total_photons_exposure_per_pixel
    # total_photons_exposure_per_pixel = (target_stiffness * get_total_photons_exposure_per_pixel) / stiffness
    # total_photons_exposure_per_pixel / pixel / photon_density

main()