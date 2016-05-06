# -*- coding: utf-8 -*-
from __future__ import absolute_import
import shutil
import traceback

from blinker import signal
from flask import current_app

from kepler.extensions import db
from kepler.models import Job, Item, get_or_create


job_failed = signal('job-failed')
job_completed = signal('job-completed')


@job_failed.connect
def failure(sender, **kwargs):
    job = kwargs['job']
    shutil.rmtree(sender.data, ignore_errors=True)
    job.status = u'FAILED'
    db.session.commit()


@job_completed.connect
def completed(sender, **kwargs):
    job = kwargs['job']
    shutil.rmtree(sender.data, ignore_errors=True)
    job.status = u'COMPLETED'
    db.session.commit()


def create_job(uri, data, task_list, access):
    item = get_or_create(Item, uri=uri, access=access)
    job = Job(item=item, status=u'PENDING')
    db.session.add(job)
    db.session.commit()
    try:
        return JobRunner(job.id, data, task_list)
    except Exception:
        job.status = u'FAILED'
        db.session.commit()
        raise


class JobRunner(object):
    def __init__(self, job_id, data, task_list):
        self.tasks = task_list
        self.job_id = job_id
        self.data = data

    def __call__(self):
        job = Job.query.get(self.job_id)
        try:
            for task in self.tasks:
                task(job, self.data)
            job_completed.send(self, job=job)
        except Exception:
            current_app.logger.warn(traceback.format_exc())
            job_failed.send(self, job=job)
            raise
