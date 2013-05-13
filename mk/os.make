include $(TOP)/mk/detectOS.make

#### Linux

ifeq ($(OS),Linux)
	OBJ_EXT = o
	LIB_EXT = a
	LIB_LINK = ar rc $(LIBRARY) $(OBJS)
	RANLIB = ranlib
	SHLIB_EXT = so
	SHLIB_LINK = $(LOADER) $(LDFLAGS) -shared -o $(SHLIB) $(OBJS) $(LIBS)
	PROG_EXT =
	PROG_LINK = $(LOADER) $(LDFLAGS) -o $(PROG) $(OBJS) $(LIBS)

ifdef DEBUG
	OPT = -g -Wall -Wextra
else
	OPT = -O3
endif
	CC = gcc -pipe -fPIC
	CXX = g++ -pipe -fPIC

	PYDEF = -fvisibility-ms-compat -DPyMODINIT_FUNC='extern "C" __attribute__((__visibility__("default"))) PyObject*'
	PYMOD_EXT = so
	PYMOD_LINK = $(LOADER) -shared -o $(PYMOD) $(OBJS) $(LIBS)
	PYTHON_LIB = -L$(libdir) -lpython$(PYTHON_VERSION)$(PYTHON_ABI)

	OPENGL_LIBS = -L$(libdir) -lGLEW -lGL

	ifdef LD_LIBRARY_PATH
		LD_LIBRARY_PATH := $(libdir):$(LD_LIBRARY_PATH)
	else
		LD_LIBRARY_PATH = $(libdir)
	endif
	export LD_LIBRARY_PATH
endif

#### Darwin, a.k.a., Apple Mac OS X

ifeq ($(OS),Darwin)
	USE_MAC_FRAMEWORKS = 1
	# *nix system
	OBJ_EXT = o
	LIB_EXT = a
	LIB_LINK = ar crs $(LIBRARY) $(OBJS)
	RANLIB = ranlib
	SHLIB_EXT = dylib
	SHLIB_LINK = $(LOADER) $(LDFLAGS) -dynamiclib -headerpad_max_install_names -install_name @executable_path/../lib/$(SHLIB) -o $(SHLIB) $(OBJS) $(LIBS)
	PROG_EXT =
	PROG_LINK = $(LOADER) $(LDFLAGS) -o $(PROG) $(OBJS) $(LIBS)

	XCODE3_SDK_ROOT = /Developer/SDKs
	XCODE4_SDK_ROOT = /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs
ifneq (,$(MACOSX_DEPLOYMENT_TARGET))
	ifneq (,$(wildcard $(XCODE4_SDK_ROOT)))
		SDK = $(XCODE4_SDK_ROOT)/MacOSX$(MACOSX_DEPLOYMENT_TARGET).sdk
	else ifneq (,$(wildcard $(XCODE3_SDK_ROOT)))
		SDK = $(XCODE3_SDK_ROOT)/MacOSX$(MACOSX_DEPLOYMENT_TARGET).sdk

	else
		$(error unable to find SDK for $(MACOSX_DEPLOYMENT_TARGET))
	endif
else ifneq (,$(wildcard $(XCODE4_SDK_ROOT)/MacOSX10.6.sdk))
	export MACOSX_DEPLOYMENT_TARGET=10.6
	SDK = $(XCODE4_SDK_ROOT)/MacOSX10.6.sdk
else ifneq (,$(wildcard $(XCODE4_SDK_ROOT)/MacOSX10.7.sdk))
	export MACOSX_DEPLOYMENT_TARGET=10.7
	SDK = $(XCODE4_SDK_ROOT)/MacOSX10.7.sdk
else ifneq (,$(wildcard $(XCODE4_SDK_ROOT)/MacOSX10.8.sdk))
	export MACOSX_DEPLOYMENT_TARGET=10.8
	SDK = $(XCODE4_SDK_ROOT)/MacOSX10.8.sdk
else ifneq (,$(wildcard $(XCODE3_SDK_ROOT)/MacOSX10.6.sdk))
	export MACOSX_DEPLOYMENT_TARGET=10.6
	SDK = $(XCODE3_SDK_ROOT)/MacOSX10.6.sdk
else
	$(error Unable to find Xcode SDK)
endif
ifdef DEBUG
	OPT = -g -Wall -Wextra
else
	OPT = -O4
endif
	CC = gcc -pipe -isysroot $(SDK)
	EXTRA_CFLAGS = -fPIC -pipe
	CXX = g++ -pipe -isysroot $(SDK)
	EXTRA_CXXFLAGS = -fPIC -fvisibility-ms-compat

	PYDEF = -DPyMODINIT_FUNC='extern "C" __attribute__((__visibility__("default"))) PyObject*'
ifdef USE_MAC_FRAMEWORKS
	PYTHON_LIB = -F$(frameworkdir) -framework Python
else
	PYTHON_LIB = -L$(libdir) -lpython$(PYTHON_VERSION)$(PYTHON_ABI)
endif
	PYMOD_EXT = so
	PYMOD_LINK = $(LOADER) -bundle -bundle_loader `which python3` -o $(PYMOD) $(OPT) $(OBJS) $(LIBS) $(PYTHON_LIB)

	OPENGL_LIBS = -L$(libdir) -lGLEW -framework OpenGL

ifdef USE_MAC_FRAMEWORKS
	ifdef DYLD_FRAMEWORK_PATH
		DYLD_FRAMEWORK_PATH := $(frameworkdir):$(DYLD_FRAMEWORK_PATH)
	else
		DYLD_FRAMEWORK_PATH = $(frameworkdir)
	endif
endif
	export DYLD_FRAMEWORK_PATH

	ifdef DYLD_FALLBACK_LIBRARY_PATH
		DYLD_FALLBACK_LIBRARY_PATH := $(libdir):$(DYLD_FALLBACK_LIBRARY_PATH)
	else
		DYLD_FALLBACK_LIBRARY_PATH = $(libdir)
	endif
	export DYLD_FALLBACK_LIBRARY_PATH
endif

# Microsoft Windows

ifeq ($(OS),Windows)
	shlibdir = $(bindir)

	OBJ_EXT = obj
	LIB_EXT = lib
	LIB_LINK = lib /OUT:$(LIBRARY) $(OBJS)
	RANLIB = :
	SHLIB_EXT = dll
	PYMOD_EXT = pyd
	SHLIB_LINK = $(CXX) $(LDFLAGS) /LD /Fe$(SHLIB) $(OBJS) $(LIBS); if [ -e $(SHLIB).manifest ]; then mt -nologo -manifest $(SHLIB).manifest -outputresource:$(SHLIB)\;2 ; fi
	PROG_EXT = .exe
	PROG_LINK = $(CXX) $(LDFLAGS) /Fe$(PROG) $(OBJS) $(LIBS); if [ -e $(PROG).manifest ]; then mt -nologo -manifest $(PROG).manifest -outputresource:$(PROG)\;1 ; fi

ifdef DEBUG
	OPT = /Zi /Wall /W3
else
	OPT = /Ox /W2
endif
	DEFS = -DWIN32
	CC = cl /nologo /Zc:forScope /EHa /GR /GF /MD
	CXX = $(CC)

	PYDEF =
	PYTHON_LIB = python$(PYVER_NODOT).$(LIB_EXT)
	PYMOD_LINK = $(CXX) $(LDFLAGS) /LD /Fe$(PYMOD) $(OBJS) $(LIBS); if [ -e $(PYMOD).manifest ]; then mt -nologo -manifest $(PYMOD).manifest -outputresource:$(PYMOD)\;2 ; fi

	OPENGL_LIBS = glew32.lib opengl32.lib

.SUFFIXES: .obj

.cpp.obj:
	$(CXX) $(CXXFLAGS) /c $<

.c.obj:
	$(CC) $(CFLAGS) /c $<
endif

PATH := $(bindir):$(PATH)
export PATH

CFLAGS = $(OPT) $(INCS) $(DEFS)
CXXFLAGS = $(OPT) $(INCS) $(DEFS)
LDFLAGS = $(OPT)
LOADER = $(CXX)

LIBRARY = lib$(LIBNAME).$(LIB_EXT)
SHLIB = lib$(LIBNAME).$(SHLIB_EXT)
PYMOD = $(PYMOD_NAME).$(PYMOD_EXT)
PROG = $(PROG_NAME)$(PROG_EXT)

NUMPY_INC += -I"$(shell python3 -c "import numpy; print numpy.get_include()")"

.SUFFIXES: .rst .html
.rst.html:
	rst2html --title=$* $^ $@

.SUFFIXES: .py .pyc .pyo
ifdef UNIX
.py.pyc:
	@rm -f $@
	python3 -t -m py_compile '$<'

.py.pyo:
	@rm -f $@
	python3 -t -OO -m py_compile '$<'
endif

ifdef WIN32
.py.pyc:
	@rm -f $@
	python3 -t -m py_compile '$(shell cygpath -m $<)'

.py.pyo:
	@rm -f $@
	python3 -t -OO -m py_compile '$(shell cygpath -m $<)'
endif

