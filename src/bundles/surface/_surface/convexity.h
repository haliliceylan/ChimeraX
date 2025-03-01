// vi: set expandtab shiftwidth=4 softtabstop=4:

/*
 * === UCSF ChimeraX Copyright ===
 * Copyright 2022 Regents of the University of California. All rights reserved.
 * The ChimeraX application is provided pursuant to the ChimeraX license
 * agreement, which covers academic and commercial uses. For more details, see
 * <https://www.rbvi.ucsf.edu/chimerax/docs/licensing.html>
 *
 * This particular file is part of the ChimeraX library. You can also
 * redistribute and/or modify it under the terms of the GNU Lesser General
 * Public License version 2.1 as published by the Free Software Foundation.
 * For more details, see
 * <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
 *
 * THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER
 * EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. ADDITIONAL LIABILITY
 * LIMITATIONS ARE DESCRIBED IN THE GNU LESSER GENERAL PUBLIC LICENSE
 * VERSION 2.1
 *
 * This notice must be embedded in or attached to all copies, including partial
 * copies, of the software or any revisions or derivations thereof.
 * === UCSF ChimeraX Copyright ===
 */

// ----------------------------------------------------------------------------
//
#ifndef CONVEXITY_HEADER_INCLUDED
#define CONVEXITY_HEADER_INCLUDED

#include <Python.h>			// use PyObject

extern "C"
{
//
// Return convexity values for each vertex defined as 2*pi - (cone angle)
// where the cone is formed by the triangles that share that vertex and
// faces toward the surface interior (counter-clockwise righthand normal
// points to exterior).  Cone angle is steradians (surface area on unit sphere).
//
// Args: vertices, triangles
// Optional args: smoothing iterations, convexity values (float64)
// Returns convexity values array (float64, same length as vertices)
//
PyObject *vertex_convexity(PyObject *s, PyObject *args, PyObject *keywds);
}

#endif
