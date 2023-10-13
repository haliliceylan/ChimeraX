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

from chimerax.core.toolshed import BundleAPI

class _MyAPI(BundleAPI):

    @staticmethod
    def register_command(command_name, logger):
        # 'register_command' is lazily called when the command is referenced
        from importlib import import_module
        command_word = command_name.split()[0]
        if command_word.startswith('~'):
            module_name = "." + command_word[1:]
        else:
            module_name = "." + command_word
        try:
            m = import_module(module_name, __package__)
        except ImportError:
            print("cannot import %s from %s" % (module_name, __package__))
        else:
            m.initialize(command_name, logger)

bundle_api = _MyAPI()
