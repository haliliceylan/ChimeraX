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

class OpenerInfo:
    """
    Bundles that can open files must implement a subclass of this class, and return it
        as the value of the bundle's BundleAPI.run_provider method.  The subclass must
        override the 'open' method of this class.
    """

    def open(self, session, data, file_name, **kw):
        """
        Return a (models, status message) tuple based on the input 'data'.  The data will
            be an opened stream unless the want_path="true" attribute was specified in this
            provider's <Provider> tag, in which case it will be a path name instead.  The
            file_name arg can be used in either case in error/status messages to identify the
            input source.

        The 'kw' dictionary will contain keywords specific to your type of open function.
            Their names and types are specified by the 'open_args' method below (which see).

        The returned models should not be added to the session by this function, that will
            occur later.  The status message typically gives information about the models
            (e.g. a structure could report the number of atoms and bonds).
        """
        raise NotImplementedError("Opener did not implement mandatory 'open' method")

    @property
    def open_args(self):
        """
        Return a dictionary that maps Python keywords used by your 'open' function to
            corresponding chimerax.core.commands.Annotation subclasses.  Annotations are used to
            convert command-line text typed by the user into appropriate Python values, e.g.
            chimerax.core.commands.BoolArg would convert 't' to True.  Some bundles also provide
            relevant Annotations, e.g. chimerax.atomic.AtomicStructureArg.
        """
        return {}

class FetcherInfo:
    """
    Bundles that can fetch files must implement a subclass of this class, and return it
        as the value of the bundle's BundleAPI.run_provider method.  The subclass must
        override the 'fetch' method of this class.
    """
    def fetch(self, session, ident, format_name, ignore_cache, **kw):
        """
        Return a (models, status message) tuple based on the given ident and, if relevant, format
            name.  The 'ignore_cache' argument is rarely used directly, but may be handed off to
            pertinent fetching utility functions (e.g. chimerax.core.fetch.fetch_file()).

        The 'kw' dictionary will contain keywords specific to your type of fetch function.
            Their names and types are specified by the 'fetch_args' method below (which see).
            The 'kw' dictionary may also contain keywords specific to the function that opens
            the fetched file, so your underlying fetching function should allow for that and
            pass unrecognized keywords on to the function used to actually open the file
            [typically session.open_command.open_data().]

        The returned models should not be added to the session by this function, that will
            occur later.  The status message typically gives information about the models
            (as returned by the functon that opened the file) and/or info about the fetching.
        """
        raise NotImplementedError("Fetcher did not implement mandatory 'fetch' method")

    @property
    def fetch_args(self):
        return {}

from .manager import NoOpenerError
from .dialog import show_open_file_dialog, set_use_native_open_file_dialog, show_open_folder_dialog

from chimerax.core.toolshed import BundleAPI

class _OpenBundleAPI(BundleAPI):

    @staticmethod
    def init_manager(session, bundle_info, name, **kw):
        """Initialize open-command manager"""
        if session.ui.is_gui:
            from . import dialog
            session.ui.triggers.add_handler('ready',
                lambda *args, ses=session: dialog.create_menu_entry(ses))
        if name == "open command":
            from . import manager
            session.open_command = manager.OpenManager(session)
            return session.open_command

    @staticmethod
    def register_command(command_name, logger):
        from . import cmd
        cmd.register_command(command_name, logger)

bundle_api = _OpenBundleAPI()
