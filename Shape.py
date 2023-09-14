
import matplotlib.pyplot as plt


class Shape:

    def __init__(self):
        pass

    def plot(self):
        # subclasses must have the get_coordinates function
        coordinates = self.get_coordinates()
        plt.plot(coordinates.get_x_coordinates(), coordinates.get_y_coordinates())
        plt.axis('square')
        plt.show()
