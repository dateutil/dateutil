"""
Release script
"""

import glob
import os
import shutil
import subprocess
import sys

import click

@click.group()
def cli():
    pass

@cli.command()
def build():
    DIST_PATH = 'dist'
    if os.path.exists(DIST_PATH) and os.listdir(DIST_PATH):
        if click.confirm('{} is not empty - delete contents?'.format(DIST_PATH)):
            shutil.rmtree(DIST_PATH)
            os.makedirs(DIST_PATH)
        else:
            click.echo('Aborting')
            sys.exit(1)

    subprocess.check_call(['python', 'setup.py', 'bdist_wheel'])
    subprocess.check_call(['python', 'setup.py', 'sdist',
                           '--formats=gztar'])

@cli.command()
def sign():
    # Sign all the distribution files
    for fpath in glob.glob('dist/*'):
        subprocess.check_call(['gpg', '--armor', '--output', fpath + '.asc',
                               '--detach-sig', fpath])

    # Verify the distribution files
    for fpath in glob.glob('dist/*'):
        if fpath.endswith('.asc'):
            continue

        subprocess.check_call(['gpg', '--verify', fpath + '.asc', fpath])


@cli.command()
@click.option('--passfile', default=None)
@click.option('--release/--no-release', default=False)
def upload(passfile, release):
    if release:
        repository='pypi'
    else:
        repository='pypitest'

    env = os.environ.copy()
    if passfile is not None:
        gpg_call = subprocess.run(['gpg', '-d', passfile],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        username, password = gpg_call.stdout.decode('utf-8').split('\n')
        env['TWINE_USERNAME'] = username
        env['TWINE_PASSWORD'] = password

    dist_files = glob.glob('dist/*')
    for dist_file in dist_files:
        if dist_file.endswith('.asc'):
            continue
        if dist_file + '.asc' not in dist_files:
            raise ValueError('Missing signature file for: {}'.format(dist_file))

    args = ['twine', 'upload', '-r', repository] + dist_files
    
    p = subprocess.Popen(args, env=env)
    p.wait()

if __name__ == "__main__":
    cli()
