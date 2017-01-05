def unix(ansible, config):
    # Install Homebrew packages
    for brew_package in config.software_brew_packages:
        ansible.homebrew(name=brew_package, state='latest')


def vim(ansible, config):
    # Install vim
    ansible.homebrew(name='vim', install_options='with-lua', state='latest')

    # Create the vim package directory
    for path in ['~/.vim', '~/.vim/bundle']:
        ansible.file(path=path, state='directory', mode='0755')

    # Install vundle package manager
    ansible.git(repo='https://github.com/gmarik/Vundle.vim.git', dest='~/.vim/bundle/Vundle.vim')

    # Install vimrc to the home directory
    ansible.copy(src='files/vim/.vimrc', dest='~', mode='0644')

    # Install all vim plugins using vundle
    ansible.command('vim +PluginInstall +qall')


def docker(ansible, config):
    # Install docker
    for package in ['docker', 'docker-machine']:
        ansible.homebrew(name=package, state='latest')

    # Create a default virtual machine to run docker images
    docker_create = ansible.command(
        'docker-machine create --driver virtualbox default',
        creates='~/.docker/machine/machines/default'
    )

    # Stop default docker machine if it was created
    if docker_create.changed:
        ansible.command('docker-machine stop default')

    # Install kitematic
    ansible.homebrew_cask(name='kitematic', state='present')


def sshfs(ansible, config):
    # Install osxfuse
    ansible.homebrew_cask(name='osxfuse', state='present')

    # Install sshfs
    ansible.homebrew(name='sshfs', state='latest')


def node_js(ansible, config):
    # Install node.js
    ansible.homebrew(name='node', state='latest')

    # Install node.js global packages
    for package in config.node_js_packages:
        ansible.npm(name=package, global_=True)


def python(ansible, config):
    # Install python 3.x
    ansible.homebrew(name='python3', state='latest')

    # Install python completion
    ansible.homebrew(name='pip-completion', state='latest')

    # Install python 3.x global packages
    for package in config.python_packages:
        ansible.pip(name=package, state='latest', executable='pip3')
