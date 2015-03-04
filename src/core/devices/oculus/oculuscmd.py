def start_oculus(session):

    oc = session.oculus
    if oc is None:
        # Create separate graphics window for rendering to Oculus Rift.
        # Don't show window until after oculus started, otherwise rendering uses wrong viewport.
        from ...ui.qt import graphicswindow as gw
        win = gw.Secondary_Graphics_Window('Oculus Rift View', session, show = False)
        # Activate opengl context before initializing oculus rift device.
        win.opengl_context.make_current()
        from .track import Oculus_Rift, Oculus_Rift_Camera_Mode
        session.oculus = oc = Oculus_Rift(session.view)
        oc.window = win
        if oc.connected:
            # Move window to oculus screen and switch to full screen mode.
            w,h = oc.display_size()
            win.full_screen(w,h)
            # Set camera mode
            cmode = Oculus_Rift_Camera_Mode(oc, win.opengl_context, win.primary_opengl_context)
            cmode.set_camera_mode(session.view.camera)
            # Set redraw timer for 1 msec to minimize dropped frames.
            # In Qt 5.2 interval of 5 or 10 mseconds caused dropped frames on 2 million triangle surface,
            # but 1 or 2 msec produced no dropped frames.
            session.main_window.graphics_window.set_redraw_interval(1)
            # Start only after window properly sized otherwise Oculus SDK 0.4.4 doesn't draw on Mac
            oc.start_event_processing()
        msg = 'started oculus head tracking ' if oc.connected else 'failed to start oculus head tracking'
        session.status(msg)
        session.info(msg)

def stop_oculus(session):

    oc = session.oculus
    if oc:
        oc.close()
        session.oculus = None
        oc.window.close()
        oc.window = None
        session.main_window.graphics_window.set_redraw_interval(10)

# -----------------------------------------------------------------------------
# Command for Hydra
#
def oculus_command(enable = None, panSpeed = None, session = None):

    if not enable is None:
        if enable:
            start_oculus(session)
        else:
            stop_oculus(session)

    if not panSpeed is None:
        oc = session.oculus
        if oc:
            oc.panning_speed = panSpeed


# -----------------------------------------------------------------------------
# Command for Chimera 2.
#
def oculus_cmd(session, enable, panSpeed = None):

    if enable:
        start_oculus2(session)
    else:
        stop_oculus2(session)

    if not panSpeed is None:
        for oc in session.oculus:
            oc.panning_speed = panSpeed

def start_oculus2(session):

    if not hasattr(session, 'oculus'):
        session.oculus = []

    if session.oculus:
        return

    # Create separate graphics window for rendering to Oculus Rift.
    # Don't show window until after oculus started, otherwise rendering uses wrong viewport.
    from ...ui.graphics import OculusGraphicsWindow
    v = session.main_view
    win = OculusGraphicsWindow(v)

    # Activate opengl context before initializing oculus rift device.
    win.opengl_context.make_current()
    from .track import Oculus_Rift, Oculus_Rift_Camera_Mode
    oc = Oculus_Rift(v)
    session.oculus.append(oc)
    oc.window = win
    if oc.connected:
        # Move window to oculus screen and switch to full screen mode.
        w,h = oc.display_size()
        win.full_screen(w,h)
        # Set camera mode
        cmode = Oculus_Rift_Camera_Mode(oc, win.opengl_context, win.primary_opengl_context)
        cmode.set_camera_mode(v.camera)
        # Set redraw timer for 1 msec to minimize dropped frames.
        # In Qt 5.2 interval of 5 or 10 mseconds caused dropped frames on 2 million triangle surface,
        # but 1 or 2 msec produced no dropped frames.
        session.ui.main_window.graphics_window.set_redraw_interval(1)
        # Start only after window properly sized otherwise Oculus SDK 0.4.4 doesn't draw on Mac
        oc.start_event_processing()
    msg = 'started oculus head tracking ' if oc.connected else 'failed to start oculus head tracking'
    log = session.logger
    log.status(msg)
    log.info(msg)

def stop_oculus2(session):

    if hasattr(session, 'oculus') and session.oculus:
        for oc in session.oculus:
            oc.close()
            oc.window.close()
            oc.window = None
        del session.oculus[:]
        session.ui.main_window.graphics_window.set_redraw_interval(10)

# -----------------------------------------------------------------------------
# Register the oculus command for Chimera 2.
#
def register_oculus_command():
    from ...cli import CmdDesc, BoolArg, FloatArg, register
    _oculus_desc = CmdDesc(required = [('enable', BoolArg)],
                           keyword = [('panSpeed', FloatArg)])
    register('oculus', _oculus_desc, oculus_cmd)
