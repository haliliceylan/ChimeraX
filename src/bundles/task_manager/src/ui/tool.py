# vim: set expandtab shiftwidth=4 softtabstop=4:
#  === UCSF ChimeraX Copyright ===
#  Copyright 2022 Regents of the University of California.
#  All rights reserved.  This software provided pursuant to a
#  license agreement containing restrictions on its disclosure,
#  duplication and use.  For details see:
#  https://www.rbvi.ucsf.edu/chimerax/docs/licensing.html
#  This notice must be embedded in or attached to all copies,
#  including partial copies, of the software or any revisions
#  or derivations thereof.
#  === UCSF ChimeraX Copyright ===
from string import capwords
from typing import Dict, Optional, Union

from Qt.QtWidgets import (
    QWidget, QVBoxLayout, QAbstractItemView
    , QLabel, QHBoxLayout, QPushButton
    , QSizePolicy
)
from Qt.QtGui import QAction

from .widgets import (
    TaskManagerTable, TaskManagerRow
    , TaskManagerTableSettings
)

from chimerax.core.commands import run
from chimerax.core.errors import UserError
from chimerax.core.session import Session
from chimerax.core.tools import ToolInstance
from chimerax.ui import MainToolWindow

_settings = None

# TODO: Listen for the Add/Remove Task Triggers

class TaskManagerTool(ToolInstance):

    SESSION_ENDURING = False
    SESSION_SAVE = True
    help = "help:/user/tools/task_manager.html"

    def __init__(self, session: Session):
        super().__init__(session, "Task Manager")
        self.default_cols = {x: True for x in ["Task", "Status", "Start Time", "Run Time", "State"]}
        self.menu_widgets = {}
        self._build_ui()

    def _build_ui(self):
        """
        Build the Task Manager GUI.
        """
        self.tool_window = MainToolWindow(self)
        parent = self.tool_window.ui_area
        # TODO: This is 100% cargo culted from seeing it elsewhere. 
        # Ask then document why we do this.
        global _settings
        if _settings is None:
            _settings = TaskManagerTableSettings(self.session, "Blastprotein")
        self.main_layout = QVBoxLayout()
        self.control_widget = QWidget(parent)

        self.control_widget.setVisible(False)

        self.table = TaskManagerTable(self.control_widget, self.default_cols, _settings, parent)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tool_window.fill_context_menu = self.fill_context_menu

        self.main_layout.addWidget(self.table)
        self.main_layout.addWidget(self.control_widget)

        self.tool_window.ui_area.closeEvent = self.closeEvent
        self.tool_window.ui_area.setLayout(self.main_layout)

        self.tool_window = MainToolWindow(self)
        parent = self.tool_window.ui_area

        main_layout = QVBoxLayout()
        menu_layout_row1 = QHBoxLayout()
        input_container_row1 = QWidget(parent)

        self.menu_widgets['help'] = QPushButton("Help", input_container_row1)

        for widget in ['help']:
            self.menu_widgets[widget].setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        # Lay the menu out
        menu_layout_row1.addWidget(self.menu_widgets['help'])

        # Functionalize the menu
        self.menu_widgets['help'].clicked.connect(lambda *, run=run, ses=self.session: run(ses, " ".join(["open", self.help])))

        input_container_row1.setLayout(menu_layout_row1)
        main_layout.addWidget(input_container_row1)

        for layout in [main_layout, menu_layout_row1]:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        
        self.tool_window.ui_area.setLayout(main_layout)

        columns = ["task", "status", "start_time", "run_time", "state"]
        self.table.data = list(self.session.tasks.values())
        for string in columns:
            self.table.add_column(capwords(string.replace('_', ' ')), data_fetch=lambda x, i=string: x)
        self.table.launch(suppress_resize=True)
        self.table.resizeColumns(max_size = 100) # pixels
        self.control_widget.setVisible(True)
    
        self.tool_window.manage('side')

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.terminate()
        self.tool_window.ui_area.close()
        self.tool_window = None

    def fill_context_menu(self, menu, x, y):
        kill_action = QAction("Kill", menu)
        pause_action = QAction("Pause", menu)
        kill_action.triggered.connect(lambda: self._run_command("kill", self.table.selected))
        pause_action.triggered.connect(lambda: self._run_command("pause", self.table.selected))
        menu.addAction(kill_action)
        menu.addAction(pause_action)

    def _run_command(self, command, job_id) -> None:
        run(self.session, "taskman %s %s" (command, job_id))

    @classmethod
    def from_snapshot(cls, session, data):
        """Initializer to be used when restoring ChimeraX sessions."""
        pass

    @classmethod
    def restore_snapshot(cls, session, data):
        return TaskManagerTool.from_snapshot(session, data)

    def take_snapshot(self, session, flags):
        data = {
            'version': 3
            , 'ToolUI': ToolInstance.take_snapshot(self, session, flags)
            , 'table_session': self.table.session_info()
            , 'params': self.params._asdict()
            , 'tool_name': self._instance_name
            , 'results': self._hits
            , 'sequences': [(key
                             , self._sequences[key][0]
                             , vars(self._sequences[key][1])
                             ) for key in self._sequences.keys()]
        }
        return data
