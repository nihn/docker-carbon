#!/usr/bin/env python

import logging
from glob import glob
from os import environ, path
from subprocess import call
from sys import argv

logging.basicConfig(level=logging.INFO)
carbon_binaries = ['carbon-cache.py', 'carbon-aggregator.py', 'carbon-relay.py']


def format_with_environment(path):
    """
    Open file and format its content with environment variables.
    :param path: path to file which should be formatted
    """
    with open(path, 'r') as f:
        content = f.read()
        new_content = content.format(**environ)

    if content != new_content:
        with open(path, 'w+') as f:
            f.write(new_content)

configs = glob(path.join(environ['GRAPHITE_CONF_DIR'], '*.conf'))


logging.info('Formatting %s with environments', ', '.join(configs))

for config in configs:
    format_with_environment(config)

if len(argv) < 2 or argv[1] not in carbon_binaries:
    logging.error('One of %s is requires as first argument',
                  ', '.join(carbon_binaries))
    exit(1)

user = environ['CARBON_USER']
pidfile = argv[1] + '.pid'

call(['chown', '-R', user, environ['WHISPER_DIR']])
call(['su', user, '-c', 'rm ~/%s' % pidfile])

command = argv[1] + " --nodaemon --pidfile ~/%s start " % pidfile + \
          ' '.join(argv[2:])

logging.info('Running `%s` as %s user', command, user)
exit(call(['su', user, '-c', command]))
