# need absolute directory for build_prefix
build_prefix = $(shell (cd "$(TOP)"; pwd))/build
bindir = $(build_prefix)/bin
includedir = $(build_prefix)/include
libdir = $(build_prefix)/lib
datadir = $(build_prefix)/share
shlibdir = $(libdir)
tmpdir = $(build_prefix)/tmp

# version numbers that leak out of prerequisites

PYTHON_VERSION = 2.7
# Windows uses python22.dll instead of libpython2.2.so
PYVER_NODOT = $(subst .,,$(PYTHON_VERSION))

include $(TOP)/mk/os.make

ifdef USE_MAC_FRAMEWORKS
frameworkdir = $(build_prefix)/Library/Frameworks
endif

ifndef WIN32
RSYNC = rsync -CrltWv --executability
else
RSYNC = $(bindir)/rsync.convert -CrlptWv
endif

PYTHON_INCLUDE_DIR = $(includedir)/python$(PYTHON_VERSION)
ifdef WIN32
PYTHON_LIBRARY_DIR = $(bindir)/Lib
pymoddir = $(bindir)/DLLs
else ifdef USE_MAC_FRAMEWORKS
PYTHON_FRAMEWORK = $(frameworkdir)/Python.framework/Versions/$(PYTHON_VERSION)
PYTHON_LIBRARY_DIR = $(PYTHON_FRAMEWORK)/lib/python$(PYTHON_VERSION)
pymoddir = $(PYTHON_LIBRARY_DIR)/lib-dynload
else
PYTHON_LIBRARY_DIR = $(libdir)/python$(PYTHON_VERSION)
pymoddir = $(PYTHON_LIBRARY_DIR)/lib-dynload
endif
PYTHON_SITE_PACKAGES = $(PYTHON_LIBRARY_DIR)/site-packages
