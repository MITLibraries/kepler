# -*- coding: utf-8 -*-
from __future__ import absolute_import
import shutil

from blinker import signal

from kepler.extensions import db
from kepler.models import Job, Item, get_or_create


job_failed = signal('job-failed')
job_completed = signal('job-completed')


@job_failed.connect
def failure(sender, **kwargs):
    shutil.rmtree(sender.data, ignore_errors=True)
    sender.job.status = u'FAILED'
    db.session.commit()


@job_completed.connect
def completed(sender, **kwargs):
    shutil.rmtree(sender.data, ignore_errors=True)
    sender.job.status = u'COMPLETED'
    db.session.commit()


def create_job(uri, data, task_list, access):
    item = get_or_create(Item, uri=uri, access=access)
    job = Job(item=item, status=u'PENDING')
    db.session.add(job)
    db.session.commit()
    try:
        return JobRunner(job, data, task_list)
    except Exception:
        job.status = u'FAILED'
        db.session.commit()
        raise


class JobRunner(object):
    def __init__(self, job, data, task_list):
        self.tasks = task_list
        self.job = job
        self.data = data

    def __call__(self):
        try:
            for task in self.tasks:
                task(self.job, self.data)
            job_completed.send(self)
        except Exception:
            job_failed.send(self)
            raise
