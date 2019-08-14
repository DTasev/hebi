# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2017 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
#  This file is part of the mantid workbench.

from webservice import const
from webservice.server import socketio
import threading
import subprocess
from savu.tomo_recon import __get_folder_name as get_folder_name
import uuid


class TalkativeSAVUProcess(threading.Thread):
    def __init__(self, data_path, process_list, output_path):
        """
        Runs a task asynchronously. Exit code is set on task finish/error.

        :param data_path: Path to the data.
        :param process_list: Path to the process list.
        :param output_path: Path where the output will be written.
        """
        # :param success_cb: Optional callback called when operation was successful
        # :param error_cb: Optional callback called when operation was not successful
        # :param finished_cb: Optional callback called when operation has finished
        super(TalkativeSAVUProcess, self).__init__()

        self.data_path = data_path
        self.process_list = process_list
        self.output_path = output_path
        self.id = str(uuid.uuid1())

        # self.success_cb = success_cb if success_cb is not None else lambda x: None
        # self.error_cb = error_cb if error_cb is not None else lambda x: None
        # self.finished_cb = finished_cb if finished_cb is not None else lambda: None

        self.exit_code = None

    def report_callback(self, output):
        socketio.emit(
            const.EVENT_JOB_STATUS,
            output,
            room='0/{}'.format(self.id),
            namespace=const.WS_NAMESPACE_JOB_STATUS)

    @staticmethod
    def _elapsed(start):
        return time.time() - start

    def run(self):
        output_subdir = get_folder_name(self.data_path)

        self._process = subprocess.Popen([
            "savu",
            self.data_path,
            self.process_list,
            self.output_path,
            "--folder",
            output_subdir,
        ], bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = self._process.stdout.readline()
            if output == '' and self._process.poll() is not None:
                break
            if output:
                self.report_callback(output)
        rc = self._process.poll()
        return rc

    def terminate(self):
        """Cancel an asynchronous execution"""
        # Implementation is based on
        # https://stackoverflow.com/questions/5019436/python-how-to-terminate-a-blocking-thread
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident),
                                                   ctypes.py_object(KeyboardInterrupt))
        time.sleep(0.1)
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
