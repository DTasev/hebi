class NoSuchJobError(RuntimeError):
    """
    Used to indicate that a job of a given identifier was not found.
    """
    pass


class JobRunner(object):
    """
    Used to start and manage (query status, terminate, etc.) Savu jobs.
    """

    def __init__(self):
        self._jobs = {}

    def close(self):
        pass

    def _add_job(self, job):
        self._jobs[job.id] = job

    def job(self, identifier):
        if identifier not in self._jobs:
            raise NoSuchJobError()

        return self._jobs[identifier]

    def start_job(self, queue, data_path, process_list, output_path):
        """
        Starts an asynchronous job
        :param queue: The queue for which the job is being submitted
        :param data_path: The path to the data
        :param process_list: The process list name
        :param output_path: The output path of the data
        """
        raise NotImplementedError()
