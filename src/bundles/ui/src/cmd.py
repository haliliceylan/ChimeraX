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

# -----------------------------------------------------------------------------
# Implementation of "ui" command.
#
def register_ui_command(logger):

    from chimerax.core.commands import CmdDesc, register
    from chimerax.core.commands import BoolArg, StringArg, NoArg

    ui_autostart_desc = CmdDesc(
        required=[('do_start', BoolArg), ('tool_name', StringArg)],
        synopsis = 'control whether a tool is launched at ChimeraX startup')
    register('ui autostart', ui_autostart_desc, ui_autostart, logger=logger)

    ui_favorite_desc = CmdDesc(
        required=[('make_favorite', BoolArg), ('tool_name', StringArg)],
        synopsis = 'control whether a tool is listed in the Favorites menu')
    register('ui favorite', ui_favorite_desc, ui_favorite, logger=logger)

    ui_dockable_desc = CmdDesc(
        required=[('dockable', BoolArg), ('tool_name', StringArg)],
        synopsis = "control whether a tool's windows can be docked")
    register('ui dockable', ui_dockable_desc, ui_dockable, logger=logger)

    ui_statusbar_desc = CmdDesc(
        required=[('show', BoolArg)],
        synopsis = "control whether main window status bar is shown or hidden")
    register('ui statusbar', ui_statusbar_desc, ui_statusbar, logger=logger)

    ui_menubar_desc = CmdDesc(
        required=[('show', BoolArg)],
        synopsis = "control whether main window menu bar is shown or hidden")
    register('ui menubar', ui_menubar_desc, ui_menubar, logger=logger)

    ui_fullscreen_desc = CmdDesc(
        required=[('show', BoolArg)],
        synopsis = "control whether main window is shown fullscreen without titlebar")
    register('ui fullscreen', ui_fullscreen_desc, ui_fullscreen, logger=logger)

    ui_tool_show_desc = CmdDesc(
        required=[('tool_name', StringArg)],
        synopsis="Show tool.  Start if necessary")
    register('ui tool show', ui_tool_show_desc, ui_tool_show, logger=logger)

    ui_tool_hide_desc = CmdDesc(
        required=[('tool_name', StringArg)],
        synopsis="Hide tool from view")
    register('ui tool hide', ui_tool_hide_desc, ui_tool_hide, logger=logger)

# -----------------------------------------------------------------------------
# Implementation of "tool" command.
#
def register_tool_command(logger):
    from chimerax.core.commands import create_alias
    create_alias('tool', 'ui tool $*', logger=logger)

# -----------------------------------------------------------------------------
#
def ui_autostart(session, do_start, tool_name):
    '''
    Control whether a tool is launched at ChimeraX startup
    '''

    settings = session.ui.settings
    autostart = settings.autostart[:]
    if do_start:
        if tool_name not in autostart:
            autostart.append(tool_name)
    else:
        while tool_name in autostart:
            autostart.remove(tool_name)
    settings.autostart = autostart
    settings.save('autostart')

# -----------------------------------------------------------------------------
#
def ui_favorite(session, make_favorite, tool_name):
    '''
    Control whether a tool is launched at ChimeraX startup
    '''

    settings = session.ui.settings
    favorites = settings.favorites[:]
    if make_favorite:
        if tool_name not in favorites:
            favorites.append(tool_name)
    else:
        while tool_name in favorites:
            favorites.remove(tool_name)
    settings.favorites = favorites
    settings.save('favorites')
    if session.ui.is_gui:
        session.ui.main_window.update_favorites_menu(session)

# -----------------------------------------------------------------------------
#
def ui_dockable(session, dockable, tool_name):
    '''
    Control whether a tool's windows are dockable
    '''

    settings = session.ui.settings
    undockable_tools = settings.undockable[:]
    if dockable:
        while tool_name in undockable_tools:
            undockable_tools.remove(tool_name)
    else:
        if tool_name not in undockable_tools:
            undockable_tools.append(tool_name)
    settings.undockable = undockable_tools
    settings.save('undockable')
    if session.ui.is_gui:
        session.ui.main_window._dockability_change(tool_name, dockable)

# -----------------------------------------------------------------------------
#
def ui_statusbar(session, show):
    '''
    Show or hide the statusbar.
    '''
    session.ui.main_window.show_statusbar(show)

# -----------------------------------------------------------------------------
#
def ui_menubar(session, show):
    '''
    Show or hide the top of window menubar.
    '''
    session.ui.main_window.show_menubar(show)

# -----------------------------------------------------------------------------
#
def ui_fullscreen(session, show):
    '''
    Show fullscreen (no titlebar) or normal mode.
    '''
    session.ui.main_window.show_fullscreen(show)

# -----------------------------------------------------------------------------
#
def ui_tool_show(session, tool_name, _show=True):
    '''
    Show a tool, or start one if none is running.

    Parameters
    ----------
    tool_name : string
    '''
    if not session.ui.is_gui:
        from chimerax.core.errors import UserError
        raise UserError("Need a GUI to show or hide tools")
    lc_tool_name = tool_name.casefold()
    ts = session.toolshed
    running_tools = session.tools.list()

    # First look for running tools whose display name
    # exactly matches tool_name, then look for ones
    # whose tool_info name exactly matches tool_name.
    tinst = [t for t in running_tools
             if t.display_name.casefold() == lc_tool_name]
    if not tinst:
        tinst = [t for t in running_tools
                 if t.tool_name.casefold() == lc_tool_name]
    if tinst:
        for ti in tinst:
            ti.display(_show)
        return

    # If showing the tool (as opposed to hiding it), look for
    # an installed tool whose name exactly matches tool_name.
    if _show:
        tools = ts.find_bundle_for_tool(tool_name, prefix_okay=False)
        if len(tools) == 1:
            bi, name = tools[0]
            bi.start_tool(session, name)
            return
        elif len(tools) > 1:
            from chimerax.core.errors import UserError
            raise UserError('Multiple installed tools named "%s"' % tool_name)
        # Did not find an exact match, fall through and keep looking

    # Look for running tools whose display name starts
    # with tool_name, then look for ones whose tool_name
    # starts with tool_name.
    tinst = [t for t in running_tools
             if t.display_name.casefold().startswith(lc_tool_name)]
    if not tinst:
        tinst = [t for t in running_tools
                 if t.tool_name.casefold().startswith(lc_tool_name)]
    if tinst:
        for ti in tinst:
            ti.display(_show)
        return

    # Look for an installed tool whose tool name starts
    # with tool_name.
    if _show:
        tools = ts.find_bundle_for_tool(tool_name, prefix_okay=True)
        if len(tools) == 1:
            bi, name = tools[0]
            bi.start_tool(session, name)
            return
        elif len(tools) > 1:
            from chimerax.core.errors import UserError
            raise UserError('Multiple installed tools found: %s' %
                            commas((repr(t[1]) for t in tools), 'and'))
        return

    from chimerax.core.errors import UserError
    # DEBUG:
    # for t in running_tools:
    #     print(t, repr(t.display_name), repr(t.tool_name),
    #           repr(t.bundle_info.name))
    raise UserError('No running or installed tool named "%s"' % tool_name)

# -----------------------------------------------------------------------------
#
def ui_tool_hide(session, tool_name, _show=True):
    '''
    Hide tool.

    Parameters
    ----------
    tool_name : string
    '''
    ui_tool_show(session, tool_name, _show=False)
