# Enable the powerline shell
powerline_path=$(python3 -c "import os, powerline; print(os.path.dirname(powerline.__file__))")
source "${powerline_path}/bindings/bash/powerline.sh"
