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

# Mouse mode to place markers on surfaces
from .ui import MouseMode
class MarkerMouseMode(MouseMode):
    name = 'place marker'
    icon_file = 'marker.png'

    def __init__(self, session):

        MouseMode.__init__(self, session)

        self.mode_name = 'place markers'
        self.bound_button = None

        self.center = False             # Place at centroid of surface

    def mouse_down(self, event):
        x,y = event.position()
        s = self.session
        v = s.main_view
        p = v.first_intercept(x,y)
        if p is None:
            c = None
        elif self.center and hasattr(p, 'triangle_pick'):
            c, vol = connected_center(p.triangle_pick)
            self.session.logger.info('Enclosed volume for marked surface: %.3g' % vol)
        else:
            c = p.position
        log = s.logger
        if c is None:
            log.status('No marker placed')
            return
        place_marker(self.session, c)

    def mouse_drag(self, event):
        pass

    def mouse_up(self, event):
        pass

def marker_settings(session):
    if not hasattr(session, '_marker_settings'):
        session._marker_settings = {
            'molecule': None,
            'next_marker_num': 1,
            'marker_chain_id': 'M',
            'color': (255,255,0,255),
            'radius': 1.0
        }
    s = session._marker_settings
    return s

def marker_molecule(session):
    ms = marker_settings(session)
    m = ms['molecule']
    if m is None or m.was_deleted:
        from .atomic import Structure
        ms['molecule'] = m = Structure(session, name = 'markers')
        m.ball_scale = 1.0
        session.models.add([m])
    return m

def place_marker(session, center):
    m = marker_molecule(session)
    a = m.new_atom('', 'H')
    a.coord = center
    ms = marker_settings(session)
    a.radius = ms['radius']
    a.color = ms['color']
    a.draw_mode = a.BALL_STYLE	# Sphere style hides bonds between markers, so use ball style.
    r = m.new_residue('mark', ms['marker_chain_id'], ms['next_marker_num'])
    r.add_atom(a)
    ms['next_marker_num'] += 1
    m.new_atoms()
    session.logger.status('Placed marker')

class MarkCenterMouseMode(MarkerMouseMode):
    name = 'mark centroid'
    icon_file = 'marker2.png'

    def __init__(self, session):
        MarkerMouseMode.__init__(self, session)
        self.center = True

def connected_center(triangle_pick):
    d = triangle_pick.drawing()
    t = triangle_pick.triangle_number
    va, ta = d.vertices, d.triangles
    from . import surface
    ti = surface.connected_triangles(ta, t)
    tc = ta[ti,:]
    varea = surface.vertex_areas(va, tc)
    a = varea.sum()
    c = varea.dot(va)/a
    cscene = d.scene_position * c
    vol, holes = surface.enclosed_volume(va, tc)
    return cscene, vol

class ConnectMouseMode(MouseMode):
    name = 'connect markers'
    icon_file = 'bond.png'

    def mouse_down(self, event):
        s = self.session
        from .atomic import selected_atoms
        atoms1 = selected_atoms(s)
        from .ui.mousemodes import mouse_select
        mouse_select(event, 'replace', s, self.view)
        atoms2 = selected_atoms(s)
        if len(atoms1) == 1 and len(atoms2) == 1:
            a1, a2 = atoms1[0], atoms2[0]
            if a1.structure != a2.structure:
                s.logger.status('Cannot connect atoms from different molecules')
            elif not a1.connects_to(a2):
                m = a1.structure
                b = m.new_bond(a1,a2)
                b.radius = 0.5*min(a1.radius, a2.radius)
                b.color = (101,156,239,255)	# cornflowerblue
                b.halfbond = False
                s.logger.status('Made connection, distance %.3g' % b.length)

def mark_map_center(volume):
    for s in volume.surface_drawings:
        va, ta = d.vertices, d.triangles
        from . import surface
        varea = surface.vertex_areas(va, ta)
        a = varea.sum()
        c = varea.dot(va)/a
        place_marker(volume.session, c)
        
