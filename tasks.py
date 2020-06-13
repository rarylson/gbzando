from invoke import task, run

import deploy_config as conf

DEPLOY_PATH = 'deploy'


@task
def publish(c):
    run("aws s3 sync {0}/ s3://{1} --delete --profile {2}".format(
        DEPLOY_PATH.rstrip('/') + '/',
        conf.s3_production,
        conf.aws_profile))


@task
def publish_homolog(c):
    run("aws s3 sync {0}/ s3://{1} --delete --profile {2}".format(
        DEPLOY_PATH.rstrip('/') + '/',
        conf.s3_homolog,
        conf.aws_profile))
