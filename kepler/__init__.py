# -*- coding: utf-8 -*-
from __future__ import absolute_import
from functools import reduce
import tempfile
import os

from werkzeug import secure_filename


def compose(*funcs):
    return reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)),
                  funcs)


def make_tempfile(data=None):
    """Create a temporary file and return the path.

    This uses ``tempfile.mkstemp`` from the standard library to create the
    tempfile. The temporary file will be removed if an exception is raised
    while trying to write the provided.

    .. note::

        It is up to you to delete the file when you are finished.

    :param data: ``werkzeug.datastructures.FileStorage`` object
    :return: absolute path to temporary file or ``None`` if no data was provided
    """

    if not data:
        return None
    filename = secure_filename(data.filename)
    fd, fname = tempfile.mkstemp(suffix="-%s" % filename)
    fp = os.fdopen(fd, 'wb')
    try:
        data.save(fp)
        fp.close()
    except:
        os.remove(fname)
        raise
    return fname
