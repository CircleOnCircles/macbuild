def unix(elite, config, printer):
    printer.info('Install brew packages.')
    for brew_package in config.software_brew_packages:
        elite.brew(name=brew_package, state='latest')


def vim(elite, config, printer):
    printer.info('Install vim.')
    elite.brew(name='vim', options='--with-lua', state='latest')

    printer.info('Create the vim package directory.')
    for path in ['~/.vim', '~/.vim/bundle']:
        elite.file(path=path, state='directory', mode='0755')

    printer.info('Install vundle package manager.')
    elite.git(repo='https://github.com/gmarik/Vundle.vim.git', path='~/.vim/bundle/Vundle.vim')

    printer.info('Install vimrc to the home directory.')
    elite.file(source='files/vim/.vimrc', path='~', mode='0644')

    printer.info('Install all vim plugins using vundle.')
    elite.run(command='vim +PluginInstall +qall')


def docker(elite, config, printer):
    printer.info('Install docker.')
    for package in ['docker', 'docker-machine']:
        elite.brew(name=package, state='latest')

    printer.info('Create a default virtual machine to run docker images.')
    docker_create = elite.run(
        command='docker-machine create --driver virtualbox default',
        creates='~/.docker/machine/machines/default'
    )

    printer.info('Stop default docker machine if it was created.')
    if docker_create.changed:
        elite.run(command='docker-machine stop default')

    printer.info('Install kitematic.')
    elite.cask(name='kitematic', state='present')


def sshfs(elite, config, printer):
    printer.info('Install osxfuse.')
    elite.cask(name='osxfuse', state='present')

    printer.info('Install sshfs.')
    elite.brew(name='sshfs', state='latest')


def node_js(elite, config, printer):
    printer.info('Install node.js.')
    elite.brew(name='node', state='latest')

    printer.info('Install node.js global packages.')
    for package in config.node_js_packages:
        elite.npm(name=package, mode='global')


def python(elite, config, printer):
    printer.info('Install python 3.x.')
    elite.brew(name='python3', state='latest')

    printer.info('Install python completion.')
    elite.brew(name='pip-completion', state='latest')

    printer.info('Install python 3.x global packages.')
    for package in config.python_packages:
        elite.pip(name=package, state='latest', executable='pip3')
