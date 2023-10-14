# vim: set expandtab shiftwidth=4 softtabstop=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2022 Regents of the University of California. All rights reserved.
# This software is provided pursuant to the ChimeraX license agreement, which
# covers academic and commercial uses. For more information, see
# <http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html>
#
# This file is part of the ChimeraX library. You can also redistribute and/or
# modify it under the GNU Lesser General Public License version 2.1 as
# published by the Free Software Foundation. For more details, see
# <https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html>
#
# This file is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. This notice
# must be embedded in or attached to all copies, including partial copies, of
# the software or any revisions or derivations thereof.
# === UCSF ChimeraX Copyright ===

from Qt.QtWidgets import QFrame, QHBoxLayout, QLabel
class SaveModelOptionWidget(QFrame):
    def __init__(self, session, name, model_type):
        super().__init__()

        mlayout = QHBoxLayout()
        mlayout.setContentsMargins(0,0,0,0)
        mlayout.setSpacing(10)
        self.setLayout(mlayout)

        self._name = name
        sm = QLabel(name)
        mlayout.addWidget(sm)
        from chimerax.ui.widgets import ModelMenuButton
        self._model_menu = mm = ModelMenuButton(session, class_filter = model_type)
        mlayout.addWidget(mm)
        mlayout.addStretch(1)    # Extra space at end

    def options_string(self):
        m = self._model_menu.value
        if m is None:
            from chimerax.core.errors import UserError
            raise UserError("No %s chosen to save" % self._name.lower())
        return 'model #%s' % m.id_string
