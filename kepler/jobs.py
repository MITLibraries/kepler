# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import partial

from blinker import signal

from kepler.models import Job, Item, get_or_create
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat
from kepler.tasks import *


job_failed = signal('job-failed')
job_completed = signal('job-completed')

shapefile_task_list = [make_record, shapefile_upload_task, index_record]
geotiff_task_list = [make_record, tiff_upload_task, index_record]
repo_task_list = [load_repo_records, index_records, ]


@job_failed.connect
def failure(sender, **kwargs):
    sender.job.status = u'FAILED'
    db.session.commit()


@job_completed.connect
def completed(sender, **kwargs):
    sender.job.status = u'COMPLETED'
    db.session.commit()


def create_job(job_type, uuid, data=None):
    item = get_or_create(Item, uri=uuid)
    job = Job(item=item, status=u'PENDING')
    db.session.add(job)
    db.session.commit()
    try:
        if job_type == 'shapefile':
            return JobRunner(tasks(shapefile_task_list), job, data=data)
        elif job_type == 'geotiff':
            return JobRunner(tasks(geotiff_task_list), job, data=data)
        else:
            raise UnsupportedFormat(job_type)
    except Exception:
        job.status = u'FAILED'
        db.session.commit()
        raise


class JobRunner(object):
    def __init__(self, task_func, job, *args, **kwargs):
        self.tasks = partial(task_func, *args, **kwargs)
        self.job = job

    def __call__(self):
        try:
            self.tasks(self.job)
            job_completed.send(self)
        except Exception:
            job_failed.send(self)
            raise
