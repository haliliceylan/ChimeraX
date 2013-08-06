// ----------------------------------------------------------------------------
// Compute linear combination of matrices.  5x faster than numpy.
//
#include <Python.h>			// use PyObject

#include "pythonarray.h"		// use array_from_python()
#include "rcarray.h"			// use Numeric_Array, Array<T>

// ----------------------------------------------------------------------------
//
template<class T>
static void lin_combine(float f1, const Reference_Counted_Array::Array<T> &m1,
			float f2, const Reference_Counted_Array::Array<T> &m2,
			const Reference_Counted_Array::Array<T> &m)
			   
{
  int n = m.size();
  T *v1 = m1.values(), *v2 = m2.values(), *v = m.values();
  for (int k = 0 ; k < n ; ++k)
	 v[k] = static_cast<T>(f1*v1[k]+f2*v2[k]);
}

// ----------------------------------------------------------------------------
// Return linear combination of 3-d arrays.
//
extern "C" PyObject *linear_combination(PyObject *s, PyObject *args, PyObject *keywds)
{
  Reference_Counted_Array::Numeric_Array m1, m2, m;
  float f1, f2;
  const char *kwlist[] = {"f1", "m1", "f2", "m2", "result", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, keywds,
				   const_cast<char *>("fO&fO&O&"), (char **)kwlist,
				   &f1, parse_3d_array, &m1, &f2, parse_3d_array, &m2,
				   parse_3d_array, &m))
    return NULL;

  if (!m1.is_contiguous() || !m2.is_contiguous() || !m.is_contiguous())
    {
      PyErr_SetString(PyExc_TypeError,
		      "linear_combination: arrays must be contiguous");
      return NULL;
    }
  if (m1.value_type() != m.value_type() || m2.value_type() != m.value_type())
    {
      PyErr_SetString(PyExc_TypeError,
		      "linear_combination: arrays must have same value type");
      return NULL;
    }

  call_template_function(lin_combine, m.value_type(), (f1, m1, f2, m2, m));

  Py_INCREF(Py_None);
  return Py_None;
}

// ----------------------------------------------------------------------------
//
template<class T>
static void inner(const Reference_Counted_Array::Array<T> &m1,
		  const Reference_Counted_Array::Array<T> &m2,
		  double *sum)
{
  double s = 0;
  int n = m1.size(), s1 = m1.stride(0), s2 = m2.stride(0);
  T *v1 = m1.values(), *v2 = m2.values();
  if (s1 == 1 && s2 == 1)
    for (int k = 0 ; k < n ; ++k)
      s += ((double)v1[k])*((double)v2[k]);
  else
    for (int k = 0 ; k < n ; ++k)
      s += ((double)v1[k*s1])*((double)v2[k*s2]);
  *sum = s;
}

// ----------------------------------------------------------------------------
// Computes sum in 64-bit, 1-d contiguous arrays only.
//
extern "C" PyObject *inner_product_64(PyObject *s, PyObject *args, PyObject *keywds)
{
  PyObject *m1py, *m2py;
  const char *kwlist[] = {"m1", "m2", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, keywds,
				   const_cast<char *>("OO"), (char **)kwlist,
				   &m1py, &m2py))
    return NULL;

  Reference_Counted_Array::Numeric_Array m1 = array_from_python(m1py, 1);
  Reference_Counted_Array::Numeric_Array m2 = array_from_python(m2py, 1);

  if (m2.size() != m1.size())
    {
      PyErr_SetString(PyExc_TypeError,
		      "inner_product_64: arrays must be same size");
      return NULL;
    }
  if (m2.value_type() != m1.value_type())
    {
      PyErr_SetString(PyExc_TypeError,
		      "inner_product_64: arrays must have same value type");
      return NULL;
    }

  double sum = 0;
  call_template_function(inner, m1.value_type(), (m1, m2, &sum));

  return PyFloat_FromDouble(sum);
}
