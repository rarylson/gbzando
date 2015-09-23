from fabric.api import *
import fabric.contrib.project as project

import os
import shutil

import deploy_config as conf

DEPLOY_PATH = 'deploy'


def clean_deploy():
    local('make clean_deploy')


@hosts(conf.production)
def publish():
    clean_deploy()
    local('make deploy')
    project.rsync_project(
        remote_dir=conf.production_path.rstrip('/') + '/',
        ssh_opts="-i {key_filename}".format(conf.key_filename),
        # Don't put drafts in production
        exclude=["drafts*"],
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )


@hosts(conf.homolog)
def publish_homolog():
    clean_deploy()
    local('make deploy_homolog')
    project.rsync_project(
        remote_dir=conf.homolog_path.rstrip('/') + '/',
        ssh_opts="-i {key_filename}".format(conf.key_filename),
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )
