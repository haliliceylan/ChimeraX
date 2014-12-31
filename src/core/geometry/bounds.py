# vim: set expandtab shiftwidth=4 softtabstop=4:


# Bounding box computations
class Bounds:

    def __init__(self, xyz_min, xyz_max):
        from numpy import ndarray, array, float32
        if isinstance(xyz_min, ndarray):
            self.xyz_min = xyz_max
        else:
            self.xyz_min = array(xyz_min, float32)
        if isinstance(xyz_max, ndarray):
            self.xyz_max = xyz_max
        else:
            self.xyz_max = array(xyz_max, float32)

    def center(self):
        return 0.5 * (self.xyz_min + self.xyz_max)

    def width(self):
        return (self.xyz_max - self.xyz_min).max()


def point_bounds(xyz, placements=[]):

    if len(xyz) == 0:
        return None

    from numpy import array, ndarray
    axyz = xyz if isinstance(xyz, ndarray) else array(xyz)

    if placements:
        from numpy import empty, float32
        n = len(placements)
        xyz0 = empty((n, 3), float32)
        xyz1 = empty((n, 3), float32)
        txyz = empty(axyz.shape, float32)
        for i, tf in enumerate(placements):
            txyz[:] = axyz
            tf.move(txyz)
            xyz0[i, :], xyz1[i, :] = txyz.min(axis=0), txyz.max(axis=0)
        xyz_min, xyz_max = xyz0.min(axis=0), xyz1.max(axis=0)
    else:
        xyz_min, xyz_max = xyz.min(axis=0), xyz.max(axis=0)

    b = Bounds(xyz_min, xyz_max)
    return b


def union_bounds(blist):
    xyz_min, xyz_max = None, None
    for b in blist:
        if b is None:
            continue
        pmin, pmax = b.xyz_min, b.xyz_max
        if xyz_min is None:
            xyz_min, xyz_max = pmin, pmax
        else:
            xyz_min = tuple(min(x, px) for x, px in zip(xyz_min, pmin))
            xyz_max = tuple(max(x, px) for x, px in zip(xyz_max, pmax))
    b = None if xyz_min is None else Bounds(xyz_min, xyz_max)
    return b


def copies_bounding_box(bounds, positions):
    if bounds is None:
        return None
    (x0, y0, z0), (x1, y1, z1) = bounds.xyz_min, bounds.xyz_max
    corners = ((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), (x1, y1, z0),
               (x0, y0, z1), (x1, y0, z1), (x0, y1, z1), (x1, y1, z1))
    b = union_bounds(point_bounds(p * corners) for p in positions)
    return b


def point_axis_bounds(points, axis):
    from numpy import dot
    pa = dot(points, axis)
    a2 = dot(axis, axis)
    b = Bounds(pa.min() / a2, pa.max() / a2)
    return b
