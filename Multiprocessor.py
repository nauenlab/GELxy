import multiprocessing
import time
import Constants

class Multiprocessor:
    def get_coordinate_sets(self, shapes):
        coordinate_sets = multiprocessing.Manager().list()
        processes = []
        for shape in shapes:
            processes.append(multiprocessing.Process(target=self.append_coordinates, args=(shape, coordinate_sets)))

        self.handle_processes(processes)
        
        return coordinate_sets
    
    @staticmethod
    def append_coordinates(shape, coordinates):
        coordinates.append(shape.get_coordinates())

    
    def handle_processes(self, processes):
        """
        Handles the execution of multiple processes in parallel.

        Args:
            processes (list): A list of processes to be executed.

        Returns:
            None
        """
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