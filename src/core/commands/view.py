# vim: set expandtab shiftwidth=4 softtabstop=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2016 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  For details see:
# http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html
# This notice must be embedded in or attached to all copies,
# including partial copies, of the software or any revisions
# or derivations thereof.
# === UCSF ChimeraX Copyright ===

from . import Annotation, AnnotationError


def view(session, objects=None, frames=None, clip=True, cofr=True, orient=False, pad=0.05):
    '''
    Move camera so the displayed models fill the graphics window.
    Also camera and model positions can be saved and restored.
    Adjust camera to view all models if objects is None.

    Parameters
    ----------
    objects : Objects
      Move camera so the bounding box of specified objects fills the window.
    frames : int
      Interpolate to the desired view over the specified number of frames.
    clip : bool
      Turn on clip planes in front and behind objects.
    cofr : bool
      Set center of rotation to center of objects.
    orient : bool
      Specifying the orient keyword moves the camera view point to
      look down the scene z axis with the x-axis horizontal and y-axis
      vertical.
    pad : float
      When making objects fit in window use a window size reduced by this fraction.
      Default value is 0.05.  Pad is ignored when restoring named views.
    '''
    v = session.main_view
    if orient:
        v.initial_camera_view()

    if objects is None:
        v.view_all(pad = pad)
        v.center_of_rotation_method = 'front center'
        cp = v.clip_planes
        cp.remove_plane('near')
        cp.remove_plane('far')
    elif isinstance(objects, NamedView):
        show_view(session, objects, frames)
    else:
        view_objects(objects, v, clip, cofr, pad)


def view_objects(objects, v, clip, cofr, pad):
    if objects.empty():
        from ..errors import UserError
        raise UserError('No objects specified.')
    disp = objects.displayed()
    b = disp.bounds()
    if b is None:
        from ..errors import UserError
        raise UserError('No displayed objects specified.')
    v.view_all(b, pad = pad)
    c, r = b.center(), b.radius()
    if cofr:
        v.center_of_rotation = c

    cp = v.clip_planes
    if clip:
        cam = v.camera
        vd = cam.view_direction()
        cp.set_clip_position('near', c - r * vd, cam)
        cp.set_clip_position('far', c + r * vd, cam)
    else:
        cp.remove_plane('near')
        cp.remove_plane('far')


def view_name(session, name):
    """Save current view as given name.

    Parameters
    ----------
    name : string
      Name the current camera view and model positions so they can be shown
      later with the "show" option.
    """
    nv = _named_views(session).views
    v = session.main_view
    models = session.models.list()
    nv[name] = NamedView(v, v.center_of_rotation, models)


def view_delete(session, name):
    """Delete named saved view.

    Parameters
    ----------
    name : string
      Name of the view.  "all" deletes all named views.
    """
    nv = _named_views(session).views
    if name == 'all':
        nv.clear()
    elif name in nv:
        del nv[name]


def show_view(session, v2, frames=None):
    """Restore the saved camera view and model positions having this name.

    Parameters
    ----------
    v2 : string
      The view to show.
    frames : int
      Interpolate to the desired view over the specified number of frames.
    """
    if frames is None:
        frames = 1
    v = session.main_view
    models = session.models.list()
    v1 = NamedView(v, v.center_of_rotation, models)
    _InterpolateViews(v1, v2, frames, session)


def view_list(session):
    """Print the named camera views in the log.

    The names are links and clicking them show the corresponding view.
    """
    nv = _named_views(session).views
    names = ['<a href="cxcmd:view %s">%s</a>' % (name, name) for name in sorted(nv.keys())]
    if names:
        msg = 'Named views: ' + ', '.join(names)
    else:
        msg = 'No named views.'
    session.logger.info(msg, is_html=True)


def _named_views(session):
    # Returns dictionary mapping name to NamedView.
    if not hasattr(session, '_named_views'):
        session._named_views = nvs = NamedViews()
        session.add_state_manager('named views', nvs)
    return session._named_views


from ..state import State
class NamedView(State):
    camera_attributes = ('position', 'field_of_view', 'field_width',
                         'eye_separation_scene', 'eye_separation_pixels')

    def __init__(self, view, look_at, models):
        camera = view.camera
        self.camera = {attr: getattr(camera, attr)
                       for attr in self.camera_attributes if hasattr(camera, attr)}
        self.clip_planes = [p.copy() for p in view.clip_planes.planes()]

        # Scene point which is focus of attention used when
        # interpolating between two views so that the focus
        # of attention stays steady as camera moves and rotates.
        self.look_at = look_at

        # Save model positions
        self.positions = pos = {}
        for m in models:
            pos[m] = m.positions

    def set_view(self, view, models):
        # Set camera
        for attr, value in self.camera.items():
            setattr(view.camera, attr, value)

        # Set clip planes.
        view.clip_planes.replace_planes([p.copy() for p in self.clip_planes])

        # Set model positions
        pos = self.positions
        for m in models:
            if m in pos:
                p = pos[m]
                if m.positions is not p:
                    m.positions = p

    # Session saving for a named view.
    version = 1
    save_attrs = [
        'camera',
        'clip_planes',
        'look_at',
        'positions',
    ]
    def take_snapshot(self, session, flags):
        data = {'view attrs': {a:getattr(self,a) for a in self.save_attrs},
                'version': self.version}
        return data

    @staticmethod
    def restore_snapshot(session, data):
        nv = NamedView.__new__(NamedView)
        for k,v in data['view attrs'].items():
            setattr(nv, k, v)
        return nv

    def reset_state(self, session):
        pass

class NamedViews(State):
    def __init__(self):
        self._views = {}	# Maps name to NamedView

    @property
    def views(self):
        return self._views

    def clear(self):
        self._views.clear()
    
    # Session saving for named views.
    version = 1
    def take_snapshot(self, session, flags):
        data = {'views': self.views,
                'version': self.version}
        return data

    @staticmethod
    def restore_snapshot(session, data):
        nvs = _named_views(session)	# Get singleton NamedViews object
        nvs._views = data['views']
        return nvs

    def reset_state(self, session):
        nvs = _named_views(session)
        nvs.clear()

class _InterpolateViews:
    def __init__(self, v1, v2, frames, session):
        self.view1 = v1
        self.view2 = v2
        self.frames = frames
        self.centers = _model_motion_centers(v1.positions, v2.positions)
        from . import motion
        motion.CallForNFrames(self.frame_cb, frames, session)

    def frame_cb(self, session, frame):
        v1, v2 = self.view1, self.view2
        v = session.main_view
        if frame == self.frames - 1:
            models = session.models.list()
            v2.set_view(v, models)
        else:
            f = frame / self.frames
            _interpolate_views(v1, v2, f, v, self.centers)


def _interpolate_views(v1, v2, f, view, centers):
    _interpolate_camera(v1, v2, f, view.camera)
    _interpolate_clip_planes(v1, v2, f, view)
    _interpolate_model_positions(v1, v2, centers, f)


def _interpolate_camera(v1, v2, f, camera):
    c1, c2 = v1.camera, v2.camera

    # Interpolate camera position
    from ..geometry import interpolate_rotation, interpolate_points
    p1, p2 = c1['position'], c2['position']
    r = interpolate_rotation(p1, p2, f)
    la = interpolate_points(v1.look_at, v2.look_at, f)
    # Look-at points in camera coordinates
    cl1 = p1.inverse() * v1.look_at
    cl2 = p2.inverse() * v2.look_at
    cla = interpolate_points(cl1, cl2, f)
    # Make camera translation so that camera coordinate look-at point
    # maps to scene coordinate look-at point r*cla + t = la.
    from ..geometry import translation
    t = translation(la - r * cla)
    camera.position = t * r

    # Interpolate field of view
    if 'field_of_view' in c1 and 'field_of_view' in c2:
        camera.field_of_view = (1 - f) * c1['field_of_view'] + f * c2['field_of_view']
    elif 'field_width' in c1 and 'field_width' in c2:
        camera.field_width = (1 - f) * c1['field_width'] + f * c2['field_width']

    camera.redraw_needed = True


def _interpolate_clip_planes(v1, v2, f, view):
    # Currently interpolate only if both states have clipping enabled and
    # clip plane scene normal is identical.
    p1 = {p.name: p for p in v1.clip_planes}
    p2 = {p.name: p for p in v2.clip_planes}
    pv = {p.name: p for p in view.clip_planes.planes()}
    from numpy import array_equal
    for name in p1:
        if name in p2 and name in pv:
            p1n, p2n, pvn = p1[name], p2[name], pv[name]
            if array_equal(p1n.normal, p2n.normal):
                pvn.normal = p1n.normal
                pvn.plane_point = (1 - f) * p1n.plane_point + f * p2n.plane_point
                # TODO: Update pv._last_distance


def _interpolate_model_positions(v1, v2, centers, f):
    # Only interplates models with positions in both views that have not changed number of instances.
    p1, p2 = v1.positions, v2.positions
    models = set(m for m, p in p1.items()
                 if m in p2 and p2[m] is not p and len(p2[m]) == len(p) and m in centers)
    for m in models:
        m.positions = _interpolated_positions(p1[m], p2[m], centers[m], f)


def _interpolated_positions(places1, places2, center, f):
    from ..geometry import Places
    pf = Places([p1.interpolate(p2, p1.inverse() * center, f)
                 for p1, p2 in zip(places1, places2)])
    return pf


# Compute common center of rotation for models that move rigidly as a group
# and have the same parent model.
def _model_motion_centers(mpos1, mpos2):
    bounds = {}
    tf_bounds = []
    for m, p1 in mpos1.items():
        if m in mpos2:
            p2 = mpos2[m]
            b = m.bounds()
            if b:
                tf = p2[0] * p1[0].inverse()
                blist = _close_transform(tf, tf_bounds, m.parent)
                blist.append(b)
                bounds[m] = blist

    from ..geometry import union_bounds
    centers = {m: union_bounds(blist).center() for m, blist in bounds.items()}
    return centers


def _close_transform(tf, tf_bounds, parent, max_rotation_angle=0.01, max_shift=1):
    tfinv = tf.inverse()
    center = (0, 0, 0)
    for bparent, tf2, blist in tf_bounds:
        if parent is bparent:
            shift, angle = (tfinv * tf2).shift_and_angle(center)
            if angle <= max_rotation_angle and shift < max_shift:
                return blist
    blist = []
    tf_bounds.append((parent, tf, blist))
    return blist


class NamedViewArg(Annotation):
    """Annotation for named views"""
    name = "a view name"

    @staticmethod
    def parse(text, session):
        from . import next_token
        token, text, rest = next_token(text)
        nv = _named_views(session).views
        if token in nv:
            return nv[token], text, rest
        raise AnnotationError("Expected a view name")

def view_initial(session, models=None):
    '''
    Set models to initial positions.

    Parameters
    ----------
    models : Models
      Set model positions to no rotation, no shift.
    '''

    if models is None:
        models = session.models.list()
    from ..geometry import Place
    for m in models:
        m.position = Place()

def view_matrix(session, camera=None, models=None, coordinate_system=None):
    '''
    Set model and camera positions. With no options positions are reported
    for the camera and all models. Positions are specified as 12-numbers,
    the rows of a 3-row, 4-column matrix where the first 3 columns are a
    rotation matrix and the last column is a translation applied after the rotation.

    Parameters
    ----------
    camera : Place
      Set the camera position.
    models : list of (Model, Place)
      Set model positions.
    coordinate_system : Place
      Treat camera and model positions relative to this coordinate system.
      If none, then positions are in scene coordinates.
    '''
    v = session.main_view
    csys = coordinate_system
    if camera is not None:
        v.camera.position = camera if csys is None else csys*camera
    if models is not None:
        for m,p in models:
            m.position = p if csys is None else csys*p

    if camera is None and models is None:
        report_positions(session)

def report_positions(session):
    c = session.main_view.camera
    lines = ['camera position: %s' % _position_string(c.position)]
    mlist = session.models.list()
    if mlist:
        mpos = ','.join('#%s,%s' % (m.id_string(), _position_string(m.position)) for m in mlist)
        lines.append('model positions: %s\n' % mpos)
    session.logger.info('\n'.join(lines))

def _position_string(p):
    return ','.join('%.5g' % x for x in tuple(p.matrix.flat))

def view_position(session, models, same_as_models):
    '''
    Change the scene position of some models to match the scene position of other models.
    If to_models is just one model then each model is positioned to match that one model.
    If to_models is more than one model, then models must consist of the same number of
    models and corresponding models in the two lists are aligned.

    Parameters
    ----------
    models : list of Model
      Models to move.
    same_as_models : list of Models
      Models are moved to align with these models.
    '''
    if len(same_as_models) == 1:
        tm = same_as_models[0]
        p = tm.position
        for m in models:
            if m is not tm:
                m.position = p
    elif len(models) != len(same_as_models):
        from ..errors import UserError
        raise UserError('Must specify equal numbers of models to align, got %d and %d'
                        % (len(models), len(same_as_models)))
    else:
        tp = [tm.position for tm in same_as_models]
        for m,p in zip(models, tp):
                m.position = p

from . import Annotation, AnnotationError
class ModelPlacesArg(Annotation):
    """Annotation for model id and positioning matrix as 12 floats."""
    name = "model positions"

    @staticmethod
    def parse(text, session):
        from . import cli
        token, text, rest = cli.next_token(text)
        fields = token.split(',')
        if len(fields) % 13:
            raise AnnotationError("Expected model id and 12 comma-separated numbers")
        mp = []
        while fields:
            tm, mtext, mrest = cli.TopModelsArg.parse(fields[0], session)
            if len(tm) == 0:
                raise AnnotationError('No models specified by "%s"' % fields[0])
            p = cli.PlaceArg.parse_place(fields[1:13])
            for m in tm:
                mp.append((m,p))
            fields = fields[13:]
        return mp, text, rest

def register_command(session):
    from . import CmdDesc, register, ObjectsArg, FloatArg
    from . import StringArg, PositiveIntArg, Or, BoolArg, NoArg
    from . import PlaceArg, ModelsArg, TopModelsArg, Or, CoordSysArg
    desc = CmdDesc(
        optional=[('objects', Or(ObjectsArg, NamedViewArg)),
                  ('frames', PositiveIntArg)],
        keyword=[('clip', BoolArg),
                 ('cofr', BoolArg),
                 ('orient', NoArg),
                 ('pad', FloatArg)],
        synopsis='adjust camera so everything is visible')
    register('view', desc, view, logger=session.logger)
    desc = CmdDesc(
        synopsis='list named views')
    register('view list', desc, view_list, logger=session.logger)
    desc = CmdDesc(
        required=[('name', StringArg)],
        synopsis='delete named view')
    register('view delete', desc, view_delete, logger=session.logger)
    desc = CmdDesc(
        required=[('name', StringArg)],
        synopsis='save view with name')
    register('view name', desc, view_name, logger=session.logger)
    desc = CmdDesc(
        optional=[('models', ModelsArg)],
        synopsis='set models to initial positions')
    register('view initial', desc, view_initial, logger=session.logger)
    desc = CmdDesc(
        keyword=[('camera', PlaceArg),
                 ('models', ModelPlacesArg),
                 ('coordinate_system', CoordSysArg)],
        synopsis='set camera and model positions')
    register('view matrix', desc, view_matrix, logger=session.logger)
    desc = CmdDesc(
        required=[('models', TopModelsArg)],
        keyword=[('same_as_models', TopModelsArg)],
        required_arguments = ['same_as_models'],
        synopsis='move models to have same scene position as another model')
    register('view position', desc, view_position, logger=session.logger)
