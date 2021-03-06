#!/usr/bin/python
#
# Copyright (C) 2014 eNovance SAS <licensing@enovance.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys

lib_path = os.path.join(os.environ["SF_ROOT"], "tests/functional")
sys.path.append(lib_path)

import yaml
import config

from utils import ManageSfUtils
from utils import GerritGitUtils
from pysflib.sfredmine import RedmineUtils
from utils import JenkinsUtils
from utils import get_cookie

# TODO: Create pads and pasties.


class SFProvisioner(object):
    """ This provider is only intended for testing
    SF backup/restore and update. It provisions some
    user datas in a SF installation based on a resourses.yaml
    file. Later those data can be checked by its friend
    the SFChecker.

    Provisioned data should remain really simple.
    """
    def __init__(self):
        with open('resources.yaml', 'r') as rsc:
            self.resources = yaml.load(rsc)
        config.USERS[config.ADMIN_USER]['auth_cookie'] = get_cookie(
            config.ADMIN_USER, config.USERS[config.ADMIN_USER]['password'])
        self.msu = ManageSfUtils(config.GATEWAY_HOST, 80)
        self.ggu = GerritGitUtils(config.ADMIN_USER,
                                  config.ADMIN_PRIV_KEY_PATH,
                                  config.USERS[config.ADMIN_USER]['email'])
        self.ju = JenkinsUtils()
        self.rm = RedmineUtils(
            config.REDMINE_URL,
            auth_cookie=config.USERS[config.ADMIN_USER]['auth_cookie'])

    def create_project(self, name):
        print " Creating project %s ..." % name
        self.msu.createProject(name, config.ADMIN_USER)

    def push_files_in_project(self, name, files):
        print " Add files(%s) in a commit ..." % ",".join(files)
        # TODO(fbo); use gateway host instead of gerrit host
        url = "ssh://%s@%s:29418/%s" % (config.ADMIN_USER,
                                        config.GATEWAY_HOST, name)
        clone_dir = self.ggu.clone(url, name, config_review=False)
        for f in files:
            file(os.path.join(clone_dir, f), 'w').write('data')
            self.ggu.git_add(clone_dir, (f,))
        self.ggu.add_commit_for_all_new_additions(clone_dir)
        self.ggu.direct_push_branch(clone_dir, 'master')

    def create_issues_on_project(self, name, amount):
        print " Create %s issue(s) for that project ..." % amount
        while(amount > 0):
            self.rm.create_issue(name, 'Issue %s' % amount)
            amount -= 1

    def create_jenkins_jobs(self, name, jobnames):
        print " Create Jenkins jobs(%s)  ..." % ",".join(jobnames)
        for jobname in jobnames:
            self.ju.create_job("%s_%s" % (name, jobname))

    def create_pads(self, amount):
        # TODO
        pass

    def create_pasties(self, amount):
        # TODO
        pass

    def provision(self):
        for project in self.resources['projects']:
            print "Create user datas for %s" % project['name']
            self.create_project(project['name'])
            self.push_files_in_project(project['name'],
                                       [f['name'] for f in project['files']])
            self.create_issues_on_project(project['name'], project['issues'])
            self.create_jenkins_jobs(project['name'],
                                     [j['name'] for j in project['jobnames']])
        self.create_pads(2)
        self.create_pasties(2)

p = SFProvisioner()
p.provision()
