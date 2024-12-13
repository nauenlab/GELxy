import multiprocessing
import time
import uuid
import psutil

MAXIMUM_PARALLEL_PROCESSES = psutil.cpu_count(logical=False)


class Multiprocessor:
    def get_coordinate_sets(self, shapes):
        coordinate_sets = multiprocessing.Manager().dict()
        processes = []
        shape_ids = []
        for shape in shapes:
            shape_id = uuid.uuid4()
            shape_ids.append(shape_id)
            processes.append(multiprocessing.Process(target=self.append_coordinates, args=(shape, shape_id, coordinate_sets)))

        self.handle_processes(processes)

        coordinate_sets_in_order = []
        for shape_id in shape_ids:
            if shape_id in coordinate_sets:
                coordinate_sets_in_order.append(coordinate_sets[shape_id])
        
        return coordinate_sets_in_order
    
    @staticmethod
    def append_coordinates(shape, shape_id, coordinates):
        coordinates[shape_id] = shape.get_coordinates()

    
    def handle_processes(self, processes):
        """
        Handles the execution of multiple processes in parallel.

        Args:
            processes (list): A list of processes to be executed.

        Returns:
            None
        """
        # Define the number of processes to run at a time
        num_processes = MAXIMUM_PARALLEL_PROCESSES

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