import glob
import os
import subprocess
import threading

from savu.tomo_recon import __get_folder_name as get_folder_name

from webservice.execution import Job, JobRunner


class LocalProcessJob(Job):
    def __init__(self, data_path, process_list, output_path):
        # We get the name of the directory as per running savu without the
        # --folder argument.
        # This allows us to know what the actual output directory will be so we
        # can determine the output data filename.
        output_subdir = get_folder_name(data_path)

        self._full_output_path = os.path.join(output_path, output_subdir)

        # TODO: can we use the local MPI version here?
        self._process = subprocess.Popen([
            "savu",
            data_path,
            process_list,
            output_path,
            "--folder",
            output_subdir,
        ], stdout=subprocess.PIPE)

    def id(self):
        return str(self._process.pid)

    def terminate(self):
        self._process.terminate()

    def running(self):
        status = self._process.poll()
        return status is None

    def successful(self):
        status = self._process.poll()
        return status == 0

    def status(self):
        status = self._process.poll()
        if status is None:
            return "running"
        return str(status)

    def output_dataset(self):
        candidate_files = glob.glob(
            os.path.join(self._full_output_path, "*_processed.nxs"))
        return None if len(candidate_files) == 0 else candidate_files[0]


class LocalProcessJobRunner(JobRunner):
    """
    Very minimal job runner that just runs jobs on the local machine.
    """

    def start_job(self, data_path, process_list, output_path):
        return self._add_job(
            LocalProcessJob(data_path, process_list, output_path))
