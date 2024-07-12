# vim: set expandtab ts=4 sw=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2022 Regents of the University of California. All rights reserved.
# The ChimeraX application is provided pursuant to the ChimeraX license
# agreement, which covers academic and commercial uses. For more details, see
# <http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html>
#
# This particular file is part of the ChimeraX library. You can also
# redistribute and/or modify it under the terms of the GNU Lesser General
# Public License version 2.1 as published by the Free Software Foundation.
# For more details, see
# <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
#
# THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER
# EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. ADDITIONAL LIABILITY
# LIMITATIONS ARE DESCRIBED IN THE GNU LESSER GENERAL PUBLIC LICENSE
# VERSION 2.1
#
# This notice must be embedded in or attached to all copies, including partial
# copies, of the software or any revisions or derivations thereof.
# === UCSF ChimeraX Copyright ===

def foldseek_coverage(session, conserved = 0):
    '''Show an image of all aligned sequences from a foldseek search, one sequence per image row.'''
    from .gui import foldseek_panel
    fp = foldseek_panel(session)
    if fp is None or len(fp.hits) == 0:
        from chimerax.core.errors import UserError
        raise UserError('No Foldseek results are shown')

    fcp = FoldseekCoveragePlot(session, fp.hits, fp.results_query_chain, conserved = conserved)
    return fcp

# -----------------------------------------------------------------------------
#
from chimerax.core.tools import ToolInstance
class FoldseekCoveragePlot(ToolInstance):

    name = 'Foldseek Sequence Coverage'
    help = 'help:user/tools/foldseek.html#coverage'

    def __init__(self, session, hits, query_chain, conserved = 0, order = 'cluster'):

        self._hits = hits
        self._query_chain = query_chain
        self._order = order
        self._conserved = conserved
        self._last_hover_xy = None

        ToolInstance.__init__(self, session, tool_name = self.name)

        from chimerax.ui import MainToolWindow
        tw = MainToolWindow(self)
        tw.fill_context_menu = self._fill_context_menu
        self.tool_window = tw
        parent = tw.ui_area

        from chimerax.ui.widgets import vertical_layout
        layout = vertical_layout(parent, margins = (5,0,0,0))

        from chimerax.ui.widgets import EntriesRow
        heading = f'Sequences for {len(hits)} Foldseek hits'
        hd = EntriesRow(parent, heading)
        self._heading = hd.labels[0]
        from Qt.QtWidgets import QSizePolicy
        hd.frame.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)  # Don't resize whole panel to fit heading
        layout.addWidget(hd.frame)

        rgb = self._sequence_image()
        self._coverage_view = gv = CoverageView(parent, rgb, self._mouse_hover)
        layout.addWidget(gv)

        tw.manage(placement=None)	# Start floating
        
    # ---------------------------------------------------------------------------
    #
    def _sequence_image(self):
        order = self._order
        if order == 'cluster':
            hits = hits_sorted_by_cluster(self._hits)
        elif order == 'evalue':
            hits = list(self._hits)
            hits.sort(key = lambda hit: hit['evalue'])
        else:
            hits = self._hits
        self._sorted_hits = hits
        self._coverage_array = _coverage_array(hits)
        rgb = _coverage_image(self._coverage_array)
        if self._conserved > 0:
            _color_conserved(self._coverage_array, rgb, self._conserved)
        return rgb
        
    # ---------------------------------------------------------------------------
    #
    def _mouse_hover(self, x, y):
        hit, res_type, res_num = self._hover_info(x, y)
        if hit and res_type:
            message = f'Hit {hit["database_full_id"]}   Query residue {res_type}{res_num}'
            self._last_hover_xy = x, y
        else:
            message = f'Sequence coverage for {len(self._hits)} Foldseek hits'
            self._last_hover_xy = None
        self._heading.setText(message)
        
    # ---------------------------------------------------------------------------
    #
    def _hover_info(self, x, y):
        query_res = self._column_query_residues()
        if y >= 0 and y < len(self._sorted_hits) and x >= 0 and x < len(query_res):
            hit = self._sorted_hits[y]
            res_type, res_num = query_res[x]
        else:
            hit = res_type = res_num = None
        return hit, res_type, res_num

    # ---------------------------------------------------------------------------
    #
    def _column_query_residues(self):
        if not hasattr(self, '_query_res'):
            qstart, qend = self._query_residue_range()
            qres = self._query_chain.existing_residues[qstart-1:qend]
            self._query_res = [(r.one_letter_code, r.number) for r in qres]
        return self._query_res

    # ---------------------------------------------------------------------------
    #
    def _query_residue_range(self):
        if not hasattr(self, '_query_res_range'):
            self._query_res_range = _query_residue_range(self._hits)
        return self._query_res_range

    # ---------------------------------------------------------------------------
    #
    def _fill_context_menu(self, menu, x, y):
        if self._last_hover_xy:
            # Use last hover position since menu post position is different by several pixels.
            hx, hy = self._last_hover_xy
            hit, res_type, res_num = self._hover_info(hx, hy)
            if hit:
                menu.addAction(f'Open structure {hit["database_full_id"]}',
                               lambda hit=hit: self._open_hit(hit))
            if res_type:
                menu.addAction(f'Select query residue {res_type}{res_num}',
                               lambda res_num=res_num: self._select_query_residue(res_num))
            menu.addSeparator()

        menu.addAction('Order by e-value', self._order_by_evalue)
        menu.addAction('Order by cluster', self._order_by_cluster)
        self._add_menu_toggle(menu, 'Color conserved', self._conserved>0, self._color_conserved)
        menu.addAction('Save image', self._save_image)
        
    # ---------------------------------------------------------------------------
    #
    def _add_menu_toggle(self, menu, text, checked, callback):
        from Qt.QtGui import QAction
        a = QAction(text, menu)
        a.setCheckable(True)
        a.setChecked(checked)
        a.triggered.connect(callback)
        menu.addAction(a)
        
    # ---------------------------------------------------------------------------
    #
    def _open_hit(self, hit):
        from .gui import foldseek_panel
        fp = foldseek_panel(self.session)
        kw = {'trim': fp.trim, 'alignment_cutoff_distance': fp.alignment_cutoff_distance} if fp else {}
        from .foldseek import open_hit
        open_hit(self.session, hit, self._query_chain, **kw)

    # ---------------------------------------------------------------------------
    #
    def _select_query_residue(self, res_num):
        resspec = self._query_chain.string(style = 'command') + f':{res_num}'
        from chimerax.core.commands import run
        run(self.session, f'select {resspec}')

    # ---------------------------------------------------------------------------
    #
    def _order_by_evalue(self):
        self._order = 'evalue'
        rgb = self._sequence_image()
        self._coverage_view.set_image(rgb)

    # ---------------------------------------------------------------------------
    #
    def _order_by_cluster(self):
        self._order = 'cluster'
        rgb = self._sequence_image()
        self._coverage_view.set_image(rgb)

    # ---------------------------------------------------------------------------
    #
    def _color_conserved(self, color = True):
        rgb = _coverage_image(self._coverage_array)
        if color:
            self._conserved = 0.30
            _color_conserved(self._coverage_array, rgb, self._conserved)
        else:
            self._conserved = 0
        self._coverage_view.set_image(rgb)

    # ---------------------------------------------------------------------------
    #
    def _save_image(self, default_suffix = '.png'):
        from os import path, getcwd
        suggested_path = path.join(getcwd(), 'coverage' + default_suffix)
        from Qt.QtWidgets import QFileDialog
        parent = self.tool_window.ui_area
        save_path, ftype  = QFileDialog.getSaveFileName(parent, 'Foldseek Coverage Image', suggested_path)
        if save_path:
            if not path.splitext(save_path)[1]:
                save_path += default_suffix
            self._coverage_view.save_image(save_path)

# ---------------------------------------------------------------------------
#
from Qt.QtWidgets import QGraphicsView
class CoverageView(QGraphicsView):
    def __init__(self, parent, rgb, hover_callback = None):
        self._hover_callback = hover_callback

        QGraphicsView.__init__(self, parent)
        from Qt.QtWidgets import QSizePolicy
        from Qt.QtCore import Qt
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        from Qt.QtWidgets import QGraphicsScene
        self._scene = gs = QGraphicsScene(self)
        self.setScene(gs)

        self._pixmap_item = None
        self.set_image(rgb)

        # Report residues and atoms as mouse hovers over plot.
        if hover_callback:
            self.setMouseTracking(True)

    def resizeEvent(self, event):
        # Rescale histogram when window resizes
        self.fitInView(self.sceneRect())
        QGraphicsView.resizeEvent(self, event)

    def mouseMoveEvent(self, event):
        if self._hover_callback:
            p = self.mapToScene(event.pos())
            x,y = p.x(), p.y()
            self._hover_callback(int(x),int(y))

    def set_image(self, rgb):
        scene = self.scene()
        pi = self._pixmap_item
        if pi is not None:
            scene.removeItem(pi)

        self._pixmap = pixmap = pixmap_from_rgb(rgb)
        self._pixmap_item = scene.addPixmap(pixmap)
        scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())

    def save_image(self, path):
        self._pixmap.save(path)

# -----------------------------------------------------------------------------
#
def _coverage_array(hits):
    qstart, qend = _query_residue_range(hits)
    qlen = qend-qstart+1

    from numpy import zeros, uint8
    cover = zeros((len(hits), qlen), uint8)
    for i,hit in enumerate(hits):
        query_coverage(hit, qstart, cover[i,:])

    return cover

# -----------------------------------------------------------------------------
#
def _query_residue_range(hits):
    qstarts = []
    qends = []
    for hit in hits:
        qstarts.append(hit['qstart'])
        qends.append(hit['qend'])
    qstart, qend = min(qstarts), max(qends)
    return qstart, qend

# -----------------------------------------------------------------------------
#
def _coverage_image(coverage_array, identity_color = (0,255,0)):
    from numpy import array, uint8
    colors = array(((255,255,255), (0,0,0), identity_color), uint8)
    rgb = colors[coverage_array]
    return rgb

# -----------------------------------------------------------------------------
#
def _color_conserved(coverage_array, rgb, conserved = 0.3, conserved_color = (255,0,0),
                     identity_color = (0,255,0)):
    for i in range(coverage_array.shape[1]):
        ci = coverage_array[:,i]
        ns,nd = (ci == 2).sum(), (ci == 1).sum()
        color = conserved_color if ns > conserved * (ns + nd) else identity_color
        rgb[ci==2,i,:] = color

# -----------------------------------------------------------------------------
#
def hits_sorted_by_cluster(hits):
    from numpy import array, float32
    intervals = array([(hit['qstart'], hit['qend']) for hit in hits], float32)

    # Cluster intervals using kmeans
    from scipy.cluster.vq import kmeans, vq
    for k in range(1,20):
        codebook, distortion = kmeans(intervals, k)
        if distortion <= 20:
            break

    # Order clusters longest interval first
    centers = list(codebook)
    centers.sort(key = lambda se: se[0]-se[1])
    labels, dist = vq(intervals, centers)

    # Sort by cluster and within a cluster by start of interval
    i = list(range(len(hits)))
    i.sort(key = lambda j: (labels[j], hits[j]['qstart']))
    shits = [hits[j] for j in i]

    return shits
    
# -----------------------------------------------------------------------------
#
def query_coverage(hit, cover_start, cover):
    qaln, taln = hit['qaln'], hit['taln']
    qi = hit['qstart']
    for qaa, taa in zip(qaln, taln):
        if qaa != '-' and taa != '-':
            cover[qi-cover_start] = 2 if taa == qaa else 1
        if qaa != '-':
            qi += 1

# -----------------------------------------------------------------------------
#
def pixmap_from_rgb(rgb):
    # Save image to a PNG file
    from Qt.QtGui import QImage, QPixmap
    h, w = rgb.shape[:2]
    im = QImage(rgb.data, w, h, 3*w, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(im)
    return pixmap
    
def register_foldseek_coverage_command(logger):
    from chimerax.core.commands import CmdDesc, register, FloatArg
    from chimerax.atomic import ChainArg
    desc = CmdDesc(
        required = [],
        keyword = [('conserved', FloatArg)],
        synopsis = 'Show an image of all aligned sequences from a foldseek search, one sequence per image row.'
    )
    register('foldseek coverage', desc, foldseek_coverage, logger=logger)
