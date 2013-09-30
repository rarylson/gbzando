from fabric.api import *
import fabric.contrib.project as project
import os

# Production options from external file
import prod_config

# Local path configuration (can be absolute or relative to fabfile)
env.content_path = 'content'
env.output_path = 'output'
env.deploy_path = 'deploy'
OUTPUT_PATH = env.output_path
DEPLOY_PATH = env.deploy_path

# Remote server configuration
production = prod_config.production
dest_path = prod_config.dest_path
env.key_filename = prod_config.key_filename

def clean():
    if os.path.isdir(OUTPUT_PATH):
        local('rm -rf {output_path}'.format(**env))
        local('mkdir {output_path}'.format(**env))

def clean_prod():
    if os.path.isdir(DEPLOY_PATH):
        local('rm -rf {deploy_path}'.format(**env))
        local('mkdir {deploy_path}'.format(**env))

def build():
    local('pelican {content_path} -o {output_path} -s pelicanconf.py'.format(**env))

def rebuild():
    clean()
    build()

def regenerate():
    local('pelican {content_path} -o {output_path} -r -s pelicanconf.py'.format(**env))

def serve():
    local('cd {output_path} && python -m SimpleHTTPServer'.format(**env))

def reserve():
    build()
    serve()

def preview():
    local('pelican {content_path} -o {deploy_path} -s publishconf.py'.format(**env))

#def cf_upload():
#    rebuild()
#    local('cd {deploy_path} && '
#          'swift -v -A https://auth.api.rackspacecloud.com/v1.0 '
#          '-U {cloudfiles_username} '
#          '-K {cloudfiles_api_key} '
#          'upload -c {cloudfiles_container} .'.format(**env))

@hosts(production)
def publish():
    local('pelican {content_path} -o {deploy_path} -s publishconf.py'.format(**env))
    project.rsync_project(
        remote_dir=dest_path,
        ssh_opts="-i {key_filename}".format(**env),
        exclude=".DS_Store",
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )
