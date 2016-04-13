import json

from flask.ext.api import status
import flask as fk

from core import app, CORE_URL, crossdomain, core_response
from refdb.common.models import SetModel
from refdb.common.models import ReferenceModel

import mimetypes
import json
import traceback
import datetime
import random
import string
import os
import thread
from StringIO import StringIO
from utils import Build

@app.route(CORE_URL + '/home', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home():
    if fk.request.method == 'GET':
        _refs = [r for r in ReferenceModel.objects()]
        _ref = _refs[-1]
        if _ref:
            if _ref.status != 'done':
                 return core_response(204, 'Nothing done', 'No graph generated yet. This reference is not finished yet.')
            else:
                file_buffer = None
                try:
                    filename = 'error-{0}.png'.format(str(_ref.id))
                    with open('plots/{0}'.format(filename), 'r') as _file:
                        file_buffer = StringIO(_file.read())
                    file_buffer.seek(0)
                except:
                    print traceback.print_exc()
                if file_buffer != None:
                    return fk.send_file(file_buffer, attachment_filename=filename, mimetype='image/png')
                else:
                    return core_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            return core_response(204, 'Nothing done', 'Could not find this reference.')
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(CORE_URL + '/home/sets', methods=['GET','POST','PUT','UPDATE','DELETE'])
@crossdomain(origin='*')
def home_sets():
    if fk.request.method == 'GET':
        refs = [r for r in ReferenceModel.objects()]
        _ref = refs[-1]
        if _ref is None:
            return core_response(404, 'Request suggested an empty response', 'Unable to find the newest reference.')
        else:
            sets = []
            for _set_id in _ref.sets['sets']:
                _set = SetModel.objects.with_id(_set_id['id'])
                if _set:
                    sets.append(_set.summary())
            return core_response(200, 'Reference [{0}] sets.'.format(str(_ref.id)), sets)
    else:
        return core_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')