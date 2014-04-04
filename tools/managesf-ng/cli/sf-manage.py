#!/usr/bin/env python

import base64
import requests as http
import json
import argparse


def validate_auth(auth):
    return len(auth.split(':')) is 2


def split_and_strip(s):
    l = s.split(',')
    return [x.strip() for x in l]

parser = argparse.ArgumentParser(
    description="Tool to manage project creation and deletion")
parser.add_argument('--host', metavar='ip-address',
                    help='Managesf host IP address', required=True)
parser.add_argument('--port', metavar='port-number',
                    help="Managesf HTTP port number", default=80)
parser.add_argument('--auth', metavar='username:password',
                    help='Authentication information', required=True)

sp = parser.add_subparsers(dest="command")
cp = sp.add_parser('create')
cp.add_argument('--name', '-n', nargs='?', metavar='project-name',
                required=True)
cp.add_argument('--description', '-d', nargs='?',
                metavar='project-description')
cp.add_argument('--upstream', '-u', nargs='?',
                metavar='GIT link')
cp.add_argument('--core-group', '-c', metavar='core-group-members',
                help='member ids separated by comma', nargs='?')
cp.add_argument('--ptl-group', '-p', metavar='ptl-group-members',
                help='member ids serarated by comma', nargs='?')

dp = sp.add_parser('delete')
dp.add_argument('--name', '-n', nargs='?', metavar='project-name',
                required=True)
args = parser.parse_args()

url = "http://%(host)s:%(port)s/project/%(name)s" % \
    {'host': args.host,
     'port': args.port,
     'name': args.name
     }

headers = {'Authorization': 'Basic ' + base64.b64encode(args.auth)}

if args.command == 'delete':
    resp = http.delete(url, headers=headers)
elif args.command == 'create':
    if not validate_auth(args.auth):
        raise Exception("'auth' should be mentioned in name:password format")

    if getattr(args, 'core_group'):
        args.core_group = split_and_strip(args.core_group)
    if getattr(args, 'ptl_group'):
        args.ptl_group = split_and_strip(args.ptl_group)
    substitute = {'description': 'description',
                  'core_group': 'core-group-members',
                  'ptl_group': 'ptl-group-members',
                  'upstream': 'upstream'
                  }
    info = {}
    for word in ['description', 'core_group', 'ptl_group', 'upstream']:
        if getattr(args, word):
            info[substitute[word]] = getattr(args, word)

    data = None
    if len(info.keys()):
        data = json.dumps(info)

    resp = http.put(url, headers=headers, data=data)

print resp.text
if resp.status_code >= 200 and resp.status_code < 203:
    print "Success"