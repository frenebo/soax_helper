# Compiling TSOAX on Ubuntu 20.04:
1. Install dependencies / libraries
   ``` bash
   $ sudo apt update && sudo apt upgrade
   $ sudo apt install git curl gcc-7 g++-7 cmake cmake-curses-gui build-essential libxt-dev mesa-utils qt5-default qtcreator qt5-doc qt5-doc-html qtbase5-doc-html qtbase5-examples qtdeclarative5-dev libboost-all-dev libegl1-mesa-dev libxcursor-dev libeigen3-dev
   ```
2. Download and compile VTK 9.1.0
   Download source code
   ``` bash
   $ curl -O -L https://github.com/Kitware/VTK/archive/refs/tags/v9.1.0.tar.gz
   $ tar -xvf v9.1.0.tar.gz
   ```
   Tell CMake to use gcc and g++ version 7
   ``` bash
   $ export CC=/usr/bin/gcc-7
   $ export CXX=/usr/bin/g++-7
   ```
   Use CMake to configure VTK build and compile
   ``` bash
   $ mkdir build_vtk && cd build_vtk
   $ ccmake ../VTK-9.1.0
   ```
   Configure VTK build with ccmake:
   - Set `CMAKE_BUILD_TYPE` to `Release`
   - Set `VTK_GROUP_ENABLE_Qt` to `Yes`
   `t` to show advanced mode settings
   - Set `VTK_LEGACY_SILENT` to `ON`
   `c` to configure until option to generate with `g` appears, press `g` to generate and exit
   Build with make:
   ``` bash
   $ make -j 4
   ```


