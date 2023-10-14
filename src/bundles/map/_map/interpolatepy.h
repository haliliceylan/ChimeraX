// vi: set expandtab shiftwidth=4 softtabstop=4:

/*
 * === UCSF ChimeraX Copyright ===
 * Copyright 2022 Regents of the University of California. All rights reserved.
 * This software is provided pursuant to the ChimeraX license agreement, which
 * covers academic and commercial uses. For more information, see
 * <http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html>
 *
 * This file is part of the ChimeraX library. You can also redistribute and/or
 * modify it under the GNU Lesser General Public License version 2.1 as
 * published by the Free Software Foundation. For more details, see
 * <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
 *
 * This file is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. This notice
 * must be embedded in or attached to all copies, including partial copies, of
 * the software or any revisions or derivations thereof.
 * === UCSF ChimeraX Copyright ===
 */

#ifndef PYINTERPOLATE_HEADER_INCLUDED
#define PYINTERPOLATE_HEADER_INCLUDED

#include <Python.h>			// use PyObject

extern "C" {

PyObject *interpolate_volume_data(PyObject *, PyObject *args);
PyObject *interpolate_volume_gradient(PyObject *, PyObject *args);
PyObject *interpolate_colormap(PyObject *, PyObject *args);
PyObject *set_outside_volume_colors(PyObject *, PyObject *args);

}

#endif
