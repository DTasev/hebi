import os
import subprocess
import threading
import uuid

from savu.tomo_recon import __get_folder_name as get_folder_name
from webservice import const
from webservice.execution import JobRunner
from webservice.server import socketio


class LocalProcessJob(threading.Thread):
    __slots__ = ('queue', 'data_path', 'process_list', 'output_path')

    def __init__(self, queue, data_path, process_list, output_path):
        super(LocalProcessJob, self).__init__()
        self.queue = queue
        self.data_path = data_path
        self.process_list = process_list

        self._all_output = []
        self.id = str(uuid.uuid1())
        self.output_path = os.path.join(output_path, self.id)
        # make the output directory
        if not os.path.isdir(self.output_path):
            os.mkdir(self.output_path)
        self.exit_code = None

    def to_dict(self):
        return {
            "id": self.id,
            "running": self.is_alive(),
            "exit_code": self.exit_code,
            "output": self.output_path,
        }

    def emit_progress(self, output):
        self._all_output.append(output)
        socketio.emit(
            const.EVENT_JOB_STATUS,
            output,
            room='{}/{}'.format(self.queue, self.id),
            namespace=const.WS_NAMESPACE_JOB_STATUS)

    def emit_end(self):
        socketio.emit(
            const.EVENT_JOB_END,
            {"message": "{} - END".format(self.id),
             "output": self.output_path},
            room='{}/{}'.format(self.queue, self.id),
            namespace=const.WS_NAMESPACE_JOB_STATUS)

    def all_output(self):
        return "\n".join(self._all_output)

    def run(self):
        output_subdir = get_folder_name(self.data_path)

        process = subprocess.Popen([
            "savu",
            self.data_path,
            self.process_list,
            self.output_path,
            "--folder",
            output_subdir,
        ], bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                self.emit_progress(output)
        self.exit_code = process.poll()

        self.emit_end()
        return self.exit_code

    # def output_dataset(self):
    #     candidate_files = glob.glob(
    #         os.path.join(self._full_output_path, "*_processed.nxs"))
    #     return None if len(candidate_files) == 0 else candidate_files[0]


class LocalProcessJobRunner(JobRunner):
    """
    Very minimal job runner that just runs jobs on the local machine.
    """

    def start_job(self, queue, data_path, process_list, output_path):
        job = LocalProcessJob(queue, data_path, process_list, output_path)
        self._add_job(job)
        job.start()
        return job.id
