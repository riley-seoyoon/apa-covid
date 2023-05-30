import multiprocessing
from functools import partial
from .parallel import parallelize

class Samprocessor:
    def __init__(self, sam_file):
        self.sam_file = sam_file
        # Initialize any necessary variables or resources

    def get_reads(self):
        # Read the SAM file and yield individual reads
        with open(self.sam_file, 'r') as sam:
            for line in sam:
                if not line.startswith('@'):  # Skip header lines
                    yield line.strip()

    def process_read(self, read):
        # Perform processing logic on a single read
        # ...

    def samprocessor_parallel(self, n_processes):
        # Create a Parallelizer instance
        parallelizer = Parallelizer(n_processes)

        # Define the tasks
        tasks = []
        for read in self.get_reads():
            task = (partial(self.process_read), (read,))
            tasks.append(task)

        # Distribute the tasks across worker processes
        results = parallelizer.map(tasks)

        # Collect the results and perform any finalization steps
        for result in results:
            # Process the result as needed
            # ...

    def finalize(self):
        # Finalize or clean up any resources

# Example usage
if __name__ == '__main__':
    sam_file = 'path/to/your/sam_file.sam'
    n_processes = multiprocessing.cpu_count()  # Use all available CPU cores

    samprocessor = Samprocessor(sam_file)
    samprocessor.samprocessor_parallel(n_processes)
    samprocessor.finalize()
