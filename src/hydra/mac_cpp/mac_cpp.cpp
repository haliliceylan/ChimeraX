#include <iostream>			// use std::cerr for debugging
#include <Python.h>			// use PyObject

#include "setfileicon.h"		// use set_file_icon
#include "touchevents.h"		// use accept_touch_events

namespace Mac_CPP
{

// ----------------------------------------------------------------------------
//
static struct PyMethodDef mac_cpp_methods[] =
{
  /* setfileicon.h */
  {const_cast<char*>("can_set_file_icon"), (PyCFunction)can_set_file_icon, METH_VARARGS|METH_KEYWORDS, NULL},
  {const_cast<char*>("set_file_icon"), (PyCFunction)set_file_icon, METH_VARARGS|METH_KEYWORDS, NULL},

  /* touchevents.h */
  {const_cast<char*>("accept_touch_events"), (PyCFunction)accept_touch_events,
   METH_VARARGS|METH_KEYWORDS, NULL},

  {NULL, NULL, 0, NULL}
};

struct module_state {
    PyObject *error;
};

#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))

static int mac_cpp_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int mac_cpp_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "mac_cpp",
        NULL,
        sizeof(struct module_state),
        mac_cpp_methods,
        NULL,
        mac_cpp_traverse,
        mac_cpp_clear,
        NULL
};

// ----------------------------------------------------------------------------
// Initialization routine called by python when module is dynamically loaded.
//
extern "C" PyObject *
PyInit_mac_cpp(void)
{
    PyObject *module = PyModule_Create(&moduledef);
    
    if (module == NULL)
      return NULL;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("mac_cpp.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}

}	// Mac_CPP namespace
