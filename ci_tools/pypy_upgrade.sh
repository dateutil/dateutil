#!/usr/bin/env bash
# Need to install an upgraded version of pypy.
if [ -f "$PYENV_ROOT/bin/pyenv" ]; then
  pushd "$PYENV_ROOT" && git pull && popd
else
  rm -rf "$PYENV_ROOT" && git clone --depth 1 https://github.com/yyuu/pyenv.git "$PYENV_ROOT"
fi

"$PYENV_ROOT/bin/pyenv" install --skip-existing "pypy-$PYPY_VERSION"
virtualenv --python="$PYENV_ROOT/versions/pypy-$PYPY_VERSION/bin/python" "$HOME/virtualenvs/pypy-$PYPY_VERSION"
source "$HOME/virtualenvs/pypy-$PYPY_VERSION/bin/activate"