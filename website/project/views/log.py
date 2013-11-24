# -*- coding: utf-8 -*-
import httplib as http
import logging

from framework import request, get_current_user
from framework.auth import get_api_key
from framework.exceptions import HTTPError

from website.project.model import NodeLog
from website.project.decorators import must_be_valid_project


logger = logging.getLogger(__name__)

def get_log(log_id):

    log = NodeLog.load(log_id)
    node_to_use = log.node
    user = get_current_user()
    api_key = get_api_key()

    if not node_to_use.can_view(user, api_key):
        raise HTTPError(http.FORBIDDEN)
    return {'log': log.serialize()}


# todo: test log visibility
@must_be_valid_project
def get_logs(*args, **kwargs):
    user = get_current_user()
    api_key = get_api_key()
    node_to_use = kwargs['node'] or kwargs['project']


    if not node_to_use.can_view(user, api_key):
        raise HTTPError(http.FORBIDDEN)
    if 'count' in request.args:
        count = int(request.args['count'])
    elif 'count' in kwargs:
        count = kwargs['count']
    elif request.json and 'count' in request.json.keys():
        count = request.json['count']
    else:
        count = 10

    # Serialize up to `count` logs in reverse chronological order; skip
    # logs that the current user / API key cannot access
    log_data = []
    chrono_logs = reversed(node_to_use.logs)
    for log in chrono_logs:
        if log and log.node.can_view(user, api_key):
            log_data.append(log.serialize())
        if len(log_data) >= count:
            break

    return {'logs': log_data}
