# Soax Helper App

# Installation
To install the latest version from this git repository, on Python3:
```  bash
$ pip3 install --user --upgrade git+https://github.com/frenebo/soax_helper.git@master
```

To tell soax helper where the batch_soax executable is, set the environment variable in your .bashrc file:
``` bash
export BATCH_SOAX_PATH=/path/to/your/SOAX_BUILD/batch_soax
```

# Warning
Soax helper expects the latest version of SOAX, which allows batch_soax to run a single data image with a single parameter. That change was made in https://github.com/tix209/SOAX on Jan 21 2022, if your version/release of batch_soax is older than that you'll have to compile it again from the newer source code.

## Compiling SOAX and TSOAX
See compiling_things.md for instructions on compiling SOAX and TSOAX.
