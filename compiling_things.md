# Compiling SOAX on macOS Big Sur

Haven't gotten it working on macOS yet...

# Compiling SOAX and TSOAX on Ubuntu 20.04:
##  1. Install dependencies and required tools
   ``` bash
   $ sudo apt update && sudo apt upgrade
   $ sudo apt install git curl gcc-7 g++-7 cmake cmake-curses-gui build-essential \
     libxt-dev mesa-utils qt5-default qtcreator qt5-doc qt5-doc-html \
     qtbase5-doc-html qtbase5-examples qtdeclarative5-dev libboost-all-dev \
     libegl1-mesa-dev libxcursor-dev libeigen3-dev
   ```
## 2. Download and compile VTK 7.1.0
   Download source code
   ``` bash
   $ curl -O -L https://github.com/Kitware/VTK/archive/refs/tags/v7.1.0.tar.gz
   $ tar -xvf v7.1.0.tar.gz
   ```
   Tell CMake to use gcc and g++ version 7
   ``` bash
   $ export CC=/usr/bin/gcc-7
   $ export CXX=/usr/bin/g++-7
   ```
   Use ccmake to configure VTK build and compile
   ``` bash
   $ mkdir build_vtk && cd build_vtk
   $ ccmake ../VTK-7.1.0
   ```
   Configure VTK build with ccmake:
   - Set `CMAKE_BUILD_TYPE` to `Release`
   - Set `VTK_GROUP_Qt` to `ON`
   - Press `c` to configure until option to generate with `g` appears, then press `g` to generate and exit.

   Build with make:
   ``` bash
   $ make
   ```
   Leave VTK build directory
   ``` bash
   $ cd ..
   ```
## 3. Download and compile ITK (not necessary for compiling just TSOAX)
   Download source code
   ``` bash
   $ curl -O -L curl -O -L  https://sourceforge.net/projects/itk/files/itk/4.7/InsightToolkit-4.7.2.tar.gz/download
   $ tar -xvf ./download
   ```
   
   Modify source code to make it compile ok:
   Add the following to vcl_compiler.h (for gcc 7.5.0) (\InsightToolkit-4.7.2\Modules\ThirdParty\VNL\src\vxl\vcl\vcl_compiler.h) at line 129
   ```
   # elif (__GNUC__==7)
   # define VCL_GCC_7
   # if (__GNUC_MINOR__ > 4 )
   # define VCL_GCC_75
   # else
   # define VCL_GCC_70
   # endif
   ```
   
   Change vcl_new.h (\InsightToolkit-4.7.2\Modules\ThirdParty\VNL\src\vxl\vcl\vcl_new.h)
   Line 19 to `# include <new>` from `# include <new.h>`
   
   Tell CMake to use gcc and g++ version 7
   ``` bash
   $ export CC=/usr/bin/gcc-7
   $ export CXX=/usr/bin/g++-7
   ```
   
   Tell CMake where to find VTK
   ``` bash
   $ export VTK_DIR=/{pathto}/build_vtk
   ```
   
   ``` bash
   $ mkdir build_itk && cd build_itk
   $ ccmake ../InsightToolkit-4.7.2/
   ```
   Configure ITK build with ccmake:
   - Set `BUILD_EXAMPLES` to `OFF`
   - Set `BUILD_TESTING` to `OFF`
   - Press `t` to show advanced mode settings
   - Set `Module_ITKVtkGlue` to `ON`
   Use ccmake to configure - press `c` to configure until generate option `g` appears, then generate.

   Build with make:
   ``` bash
   $ make
   ```

   Leave ITK build directory
   ``` bash
   $ cd ..
   ```
## 4. Download and compile SOAX
   Download source code
   ```  bash
   $ git clone https://github.com/tix209/SOAX
   ```

   Tell CMake where to find ITK
   ``` bash
   $ export ITK_DIR=/{pathto}/build_itk
   ```

   Set up SOAX buile and compile
   ``` bash
   $ mkdir build_soax && cd build_soax
   $ ccmake ../SOAX
   ```
   Use ccmake to configure - press `c` to configure until generate option `g` appears, then generate.

   Build with make:
   ``` bash
   $ make
   ```
## 5. Download and compile TSOAX
   Download source code
   ``` bash
   $ git clone --recursive https://github.com/tix209/TSOAX.git
   ```
   Modify source code of TSOAX to play nice with the latest VTK:
   - In `TSOAX/include/main_window.h`:
     - Remove the line with the declaration `class QVTKOpenGLWidget;`
     - Insert new line `#include "QVTKOpenGLWidget.h"` under the line `#include <QMainWindow>`
   - In `TSOAX/include/viewer.h`:
     - Remove the line with the declaration `class QVTKOpenGLWidget;`
     - Insert new line `#include "QVTKOpenGLWidget.h"` under the line `#include <QObject>`
   - In `TSOAX/src/viewer.cc`:
     - Remove the line `#include "QVTKWidget.h"`

   Tell CMake where to find VTK
   ``` bash
   $ export VTK_DIR=/{pathto}/build_vtk
   ```
   Set up TSOAX build and compile
   ``` bash
   $ mkdir build_tsoax && cd build_tsoax
   $ cmake -DCMAKE_BUILD_TYPE=Release ../TSOAX
   $ make
   ```

   The `TSOAX` executable should be in `build_tsoax/src`
