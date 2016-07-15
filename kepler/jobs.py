# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import shutil
import tempfile
import traceback

from flask import current_app

from kepler.bag import unpack, get_datatype
from kepler.extensions import db, s3
from kepler.models import Job, Item, get_or_create
from kepler.tasks import (index_shapefile, upload_shapefile, index_geotiff,
                          upload_geotiff, submit_to_dspace)


def fetch_bag(bucket, key):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    s3.client.download_file(bucket, key, tmp.name)
    return tmp.name


def delete_bag(bucket, key):
    s3.client.delete_object(Bucket=bucket, Key=key)


def create_job(uri):
    item = get_or_create(Item, uri=uri)
    job = Job(item=item, status=u'CREATED')
    db.session.add(job)
    db.session.commit()
    return job


def run_job(id):
    job = Job.query.get(id)
    bucket = current_app.config['S3_BUCKET']
    key = job.item.uri
    data = fetch_bag(bucket, key)
    tmpdir = tempfile.mkdtemp()
    try:
        bag = unpack(data, tmpdir)
        datatype = get_datatype(bag)
        if datatype == 'shapefile':
            tasks = [upload_shapefile, index_shapefile, ]
        elif datatype == 'geotiff':
            tasks = [upload_geotiff, submit_to_dspace, index_geotiff, ]
        else:
            raise UnsupportedFormat(datatype)
        for task in tasks:
            task(job, bag)
        job.status = u'PENDING'
    except:
        job.status = u'FAILED'
        raise
        current_app.logger.warn(traceback.format_exc())
    finally:
        db.session.commit()
        shutil.rmtree(tmpdir, ignore_errors=True)
        os.remove(data)
        delete_bag(bucket, key)
