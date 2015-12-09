# =============================================================================
# Copyright (c) 2015, Cisco Systems, Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# =============================================================================
import time
import threading

from multiprocessing import Manager
from process_pool import Pool


class JobManager(threading.Thread):
    def __init__(self, num_workers, worker_name):
        threading.Thread.__init__(self, name=worker_name)

        self.pool = Pool(num_workers=num_workers, name=worker_name)
        self.in_progress_jobs = Manager().list()
        self.lock = Manager().Lock()

    def run(self):
        while 1:
            time.sleep(20)
            self.dispatch()

    def dispatch(self):
        raise NotImplementedError("Children must override dispatch()")

    def submit_job(self, work_unit):
        with self.lock:
            if work_unit.get_unique_key() in self.in_progress_jobs:
                return False

            self.in_progress_jobs.append(work_unit.get_unique_key())

        # Remember these shared memory references
        work_unit.in_progress_jobs = self.in_progress_jobs
        work_unit.lock = self.lock

        self.pool.submit(work_unit)

        return True
