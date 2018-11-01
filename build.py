# coding=utf-8

import click
import os
import subprocess
import io

import pybee
from pybee.path import working_dir

current_dir = os.path.abspath(os.getcwd())
script_dir = os.path.abspath(os.path.dirname(__file__))

build_dir = os.path.join(script_dir, 'build')
dist_dir = os.path.join(script_dir, 'dist')

download_dir = '' 
linux_dest_dir = ''

dist_file_name=''

def prepare(arch):
    global download_dir
    global linux_dest_dir
    global dist_file_name

    download_dir = os.path.join(build_dir,
            arch, 'download'
            )
    linux_dest_dir = os.path.join(build_dir,
            arch, 'wsl-dist'
            )

    dist_file_name = 'manjaro-linux-wsl-%s-%s.tar.gz' % (
            arch, pybee.get_curr_date_time('%Y-%m-%d') 
            )

    pybee.path.mkdir(download_dir, True)
    pybee.path.mkdir(linux_dest_dir, True)
    pybee.path.mkdir(dist_dir, False)

    pybee.shell.exec(
            ['chmod', '+x',
                './manjaro-bootstrap/manjaro-bootstrap.sh'
            ]
            )


def make_bootstrap(arch, repo):
    cmd_list = [
            './manjaro-bootstrap/manjaro-bootstrap.sh',
            '-a', arch,
            '-r', repo,
            '-d', download_dir,
            linux_dest_dir
            ]
    pybee.shell.exec(
            cmd_list
            )
def append_text_to_file(fpath, text, encoding='utf-8'):
    with io.open(fpath, 'a',encoding=encoding) as f:
        f.write(text)

def exec_command_in_chroot_env(dest_dir, cmd, **kwargs):
    chroot_cmd_list = ['chroot', dest_dir, ]
    c = None
    if type(cmd) is str:
        chroot_cmd_list.append(cmd)
        c = ' '.join(chroot_cmd_list)
    else:
        chroot_cmd_list.extend(cmd)
        c = chroot_cmd_list

    pybee.shell.exec(c, **kwargs)

def make_wsl_linux_dist():
    with working_dir(os.path.join(script_dir, 'configs')):
        pybee.path.copyfiles(
                ['os-release', 'issue'],
                os.path.join(linux_dest_dir, 'etc')
                )

    append_text_to_file(
            os.path.join(linux_dest_dir, 'etc', 'locale.gen'),
            '\nen_US.UTF-8 UTF-8'
            )
    exec_command_in_chroot_env(linux_dest_dir, ['locale-gen'])

    with working_dir(os.path.join(script_dir, 'configs', 'profile.d')):
        pybee.path.copyfiles(
                ['display.sh', 'wsl.sh'],
                os.path.join(linux_dest_dir, 'etc', 'profile.d')
                )

def pack():

    print('')
    print('tar %s .....' % linux_dest_dir)
    p = os.path.join(dist_dir, dist_file_name)
    if os.path.isfile(p):
        os.unlink(p)

    with working_dir(linux_dest_dir):
        cmd = ' '.join(
                ['tar', '--ignore-failed-read', 
                    '-czvf', p, '*']
                )
        pybee.shell.exec(
                cmd, shell=True
                )
    print('finish, dist file is %s' % p)

@click.command()
@click.option('-a','--arch', default='x86_64')
@click.option('-r', '--repo', default='https://mirrors.tuna.tsinghua.edu.cn/manjaro')
def main(arch, repo):

    prepare(arch)

    make_bootstrap(arch, repo)

    make_wsl_linux_dist()

    pack()

if __name__ == '__main__':
    main()