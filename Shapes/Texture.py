from Coordinate import Coordinate, Coordinates
import Constants
import multiprocessing
import time
from copy import copy

class Texture:

    def __init__(self, shape, rows, columns):
        self.shape = shape
        self.rows = rows
        self.columns = columns

    def get_coordinates(self):
        bound = Constants.MOTOR_MAX_TRAVEL
        coordinates = Coordinates()
        x_dist = (bound / self.rows) / 2
        y_dist = (bound / self.rows) / 2
        manager = multiprocessing.Manager()
        cds = manager.list()
        cds.extend([None] * (self.rows * self.columns))
        
        processes = []
        for i in range(self.rows):
            for j in range(self.columns):
                x = x_dist * (i) + x_dist
                y = y_dist * (j) + y_dist
                self.shape.center = Coordinate(x, y)
                shape_copy = copy(self.shape)
                processes.append(multiprocessing.Process(target=self.append_coordinates, args=(i*self.rows+j, shape_copy, cds)))

        self.handle_processes(processes)
        
        for i in cds:
            coordinates += i
        
        return coordinates

    def append_coordinates(self, i, shape, coordinates):
        coordinates[i] = shape.get_coordinates()

    def handle_processes(self, processes):
        # Define the number of processes to run at a time
        num_processes = Constants.MAXIMUM_PARALLEL_PROCESSES
        
        # Start the first set of processes
        current_processes = []
        for i in range(num_processes):
            if processes:
                current_processes.append(processes.pop(0))
                current_processes[-1].start()
        
        # Loop until all processes have finished
        while current_processes:
            for thread in current_processes:
                if not thread.is_alive():
                    current_processes.remove(thread)    
                    thread.join()

                    # Start a new thread if there are any left in the queue
                    if processes:
                        new_thread = processes.pop(0)
                        current_processes.append(new_thread)
                        new_thread.start()
                    break
            time.sleep(0.5)