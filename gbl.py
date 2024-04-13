import Constants
import time


def handle_processes(processes):
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
