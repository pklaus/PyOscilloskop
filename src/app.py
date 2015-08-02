#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import Bottle, route, run, post, get, request, response, redirect, error, abort, static_file, TEMPLATE_PATH, Jinja2Template, url
from bottle import jinja2_template as template, jinja2_view as view

#import json
#import time
import os
#from datetime import datetime
#import string
#import re
#from posts import Posts
#import markdown
import logging

logger = logging.getLogger(__name__)

TEMPLATE_PATH.append(os.path.join(os.path.split(os.path.realpath(__file__))[0],'views'))

### Global objects
POSTS = object()
DEFAULT_CONTEXT = {
  'scope_name': 'Rigol Oscilloscope'
}

### The plugin

from rigolScope import RigolScope
from rigolDevice import RigolError
import inspect

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
            self.scope = RigolScope()
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
    return static_file(path, root='./static')

@interface.route('/')
@view('home.jinja2')
def home():
    return dict(active='home')

@interface.route('/robots.txt')
def robots():
    response.content_type = 'text/plain'
    return "User-agent: *\n{0}: /".format('Disallow')

def main():
    global POSTS, DEFAULT_CONTEXT, ALLOW_CRAWLING
    import argparse
    parser = argparse.ArgumentParser( 
      description='Run a web servers for your Rigol Scope' )
    parser.add_argument('-p', '--port', type=int, default=8080,
      help='The port to run the web server on.')
    parser.add_argument('-6', '--ipv6', action='store_true',
      help='Listen to incoming connections via IPv6 instead of IPv4.')
    parser.add_argument('-d', '--debug', action='store_true',
      help='Start in debug mode (with verbose HTTP error pages.')
    parser.add_argument('--scope-name', help='Name of the oscilloscope to display.')
    parser.add_argument('device', help='The /dev/usbtmc0 -like device name.')
    args = parser.parse_args()

    if args.scope_name : DEFAULT_CONTEXT['scope_name'] = args.scope_name
    Jinja2Template.defaults = DEFAULT_CONTEXT


    api.install(RigolPlugin())
    interface.mount('/api', api)
    app = interface

    if args.debug and args.ipv6:
        args.error('You cannot use IPv6 in debug mode, sorry.')
    if args.debug:
        run(app, host='0.0.0.0', port=args.port, debug=True, reloader=True)
    else:
        if args.ipv6:
            # CherryPy is Python3 ready and has IPv6 support:
            run(app, host='::', server='cherrypy', port=args.port)
        else:
            run(app, host='0.0.0.0', server='cherrypy', port=args.port)

if __name__ == '__main__':
    main()

