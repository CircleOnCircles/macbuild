def unix(ansible, config):
    ansible.info('Install Homebrew packages.')
    for brew_package in config.software_brew_packages:
        ansible.homebrew(name=brew_package, state='latest')


def vim(ansible, config):
    ansible.info('Install vim.')
    ansible.homebrew(name='vim', install_options='with-lua', state='latest')

    ansible.info('Create the vim package directory.')
    for path in ['~/.vim', '~/.vim/bundle']:
        ansible.file(path=path, state='directory', mode='0755')

    ansible.info('Install vundle package manager.')
    ansible.git(repo='https://github.com/gmarik/Vundle.vim.git', dest='~/.vim/bundle/Vundle.vim')

    ansible.info('Install vimrc to the home directory.')
    ansible.copy(src='files/vim/.vimrc', dest='~', mode='0644')

    ansible.info('Install all vim plugins using vundle.')
    ansible.command('vim +PluginInstall +qall')


def docker(ansible, config):
    ansible.info('Install docker.')
    for package in ['docker', 'docker-machine']:
        ansible.homebrew(name=package, state='latest')

    ansible.info('Create a default virtual machine to run docker images.')
    docker_create = ansible.command(
        'docker-machine create --driver virtualbox default',
        creates='~/.docker/machine/machines/default'
    )

    ansible.info('Stop default docker machine if it was created.')
    if docker_create.changed:
        ansible.command('docker-machine stop default')

    ansible.info('Install kitematic.')
    ansible.homebrew_cask(name='kitematic', state='present')


def sshfs(ansible, config):
    ansible.info('Install osxfuse.')
    ansible.homebrew_cask(name='osxfuse', state='present')

    ansible.info('Install sshfs.')
    ansible.homebrew(name='sshfs', state='latest')


def node_js(ansible, config):
    ansible.info('Install node.js.')
    ansible.homebrew(name='node', state='latest')

    ansible.info('Install node.js global packages.')
    for package in config.node_js_packages:
        ansible.npm(name=package, global_=True)


def python(ansible, config):
    ansible.info('Install python 3.x.')
    ansible.homebrew(name='python3', state='latest')

    ansible.info('Install python completion.')
    ansible.homebrew(name='pip-completion', state='latest')

    ansible.info('Install python 3.x global packages.')
    for package in config.python_packages:
        ansible.pip(name=package, state='latest', executable='pip3')
