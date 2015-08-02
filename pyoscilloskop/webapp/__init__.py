#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import inspect
import logging

from pyoscilloskop import RigolScope
from pyoscilloskop import RigolError

from bottle import Bottle, route, run, post, get, request, response, redirect, error, abort, static_file, TEMPLATE_PATH, Jinja2Template, url
from bottle import jinja2_template as template, jinja2_view as view

logger = logging.getLogger(__name__)

# Find out where our resource files are located:
try:
    from pkg_resources import resource_filename, Requirement, require
    PATH = resource_filename("pyoscilloskop", "webapp")
except:
    PATH = './'

TEMPLATE_PATH.insert(0, os.path.join(PATH, 'views'))

### Global objects
POSTS = object()
DEFAULT_CONTEXT = {
  'scope_name': 'Rigol Oscilloscope'
}

Jinja2Template.defaults = DEFAULT_CONTEXT

### The plugin

class RigolPlugin(object):
    ''' This plugin passes an sqlite3 database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. '''

    name = 'rigol'
    api = 2

    def __init__(self, usbtmc_file=None, keyword='scope'):
         self.usbtmc_file = usbtmc_file
         self.keyword = keyword

    def setup(self, app):
        try:
            self.scope = RigolScope(self.usbtmc_file)
        except RigolError as e:
            logger.error(e)
        ## To get more debug output, do:
        #scope.debugLevel = 5
        for other in app.plugins:
            if not isinstance(other, RigolPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another Rigol plugin with "\
                "conflicting settings (non-unique keyword).")

    def apply(self, callback, context):
        keyword = self.keyword
        # Test if the original callback accepts our keyword.
        # Ignore it if it does not need the plugin.
        args = inspect.getargspec(context.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Add the connection handle as a keyword argument.
            kwargs[keyword] = self.scope

            try:
                rv = callback(*args, **kwargs)
            except RigolError as e:
                raise HTTPError(500, "Rigol Plugin Error", e)
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper


### The Bottle() web application
api = Bottle()
interface = Bottle()

@api.route('/capture')
def current_trace(scope):
    ret_dict = {}
    try:
        channel_1 = scope.getChannel1()
        channel_1_data = channel_1.getData()
        ret_dict['channel1Data'] = channel_1_data.tolist()
        ret_dict['channel1Scale'] = channel_1.getVoltageScale()
        ret_dict['channel1Offset'] = channel_1.getVoltageOffset()
        channel_2 = scope.getChannel2()
        channel_2_data = channel_2.getData()
        ret_dict['channel2Data'] = channel_2_data.tolist()
        ret_dict['channel2Scale'] = channel_2.getVoltageScale()
        ret_dict['channel2Offset'] = channel_2.getVoltageOffset()
        time_axis = scope.getTimeAxis()
        time_values = time_axis.getTimeAxis()
        ret_dict['timeData'] = time_values.tolist()
        ret_dict['timeAxisMin'] = time_values.min()
        ret_dict['timeAxisMax'] = time_values.max()
        ret_dict['timeAxisUnit'] = time_axis.getUnit()
        scope.reactivateControlButtons()
    except Exception as e:
        abort(500, str(type(e)))
    return ret_dict

@interface.route('/static/<path:path>')
def static(path):
    return static_file(path, root=os.path.join(PATH, 'static'))

@interface.route('/')
@view('home.jinja2')
def home():
    return dict(active='home')

@interface.route('/robots.txt')
def robots():
    response.content_type = 'text/plain'
    return "User-agent: *\n{0}: /".format('Disallow')

