# -*- coding: utf-8 -*-
from __future__ import absolute_import

from blinker import signal

from kepler.models import Job, Item, get_or_create
from kepler.extensions import db
from kepler.exceptions import UnsupportedFormat
from kepler.tasks import *


job_failed = signal('job-failed')
job_completed = signal('job-completed')

shapefile_task_list = [upload_shapefile, index_shapefile, ]
geotiff_task_list = [upload_geotiff, index_geotiff, ]
repo_task_list = [index_repo_records, ]


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
            return JobRunner(job, data, shapefile_task_list)
        elif job_type == 'geotiff':
            return JobRunner(job, data, geotiff_task_list)
        elif job_type == 'repo':
            return JobRunner(job, data, repo_task_list)
        else:
            raise UnsupportedFormat(job_type)
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
