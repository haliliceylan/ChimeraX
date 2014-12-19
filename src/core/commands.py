# vim: set expandtab shiftwidth=4 softtabstop=4:
"""
commands -- Default set of commands
===================================

This module implements a default set of cli commands.
After importing this module, :py:func:`register`
must be called to get the commands recognized by the command line interface
(:py:mod:`chimera2.cli`).
"""

from . import cli

def pwd(session):
    import os
    print('current working directory:', os.getcwd())
_pwd_desc = cli.CmdDesc()


def exit(session):
    session.ui.quit()
_exit_desc = cli.CmdDesc()


def stop(session, ignore=None):
    raise cli.UserError('use "exit" or "quit" instead of "stop"')
_stop_desc = cli.CmdDesc(optional=[('ignore', cli.RestOfLine)])


def echo(session, text=''):
    print(text)
_echo_desc = cli.CmdDesc(optional=[('text', cli.RestOfLine)])


def open(session, filename, id=None):
    try:
        return session.models.open(filename, id=id)
    except OSError as e:
        raise cli.UserError(e)
_open_desc = cli.CmdDesc(required=[('filename', cli.StringArg)],
                         keyword=[('id', cli.ModelIdArg)])


def close(session, model_id):
    try:
        return session.models.close(model_id)
    except ValueError as e:
        raise cli.UserError(e)
_close_desc = cli.CmdDesc(required=[('model_id', cli.ModelIdArg)])


def list(session):
    models = session.models.list()
    if len(models) == 0:
        return "No open models."
    info = "Open models:"
    if len(models) > 1:
        info += ", ".join(str(m.id) for m in models[:-1]) + " and"
    info += " %s" % models[-1].id
    print(info)
_list_desc = cli.CmdDesc()


def register(session):
    """Register common cli commands"""
    cli.register('open', _open_desc, open)
    cli.register('close', _close_desc, close)
    cli.register('list', _list_desc, list)
    cli.register('exit', _exit_desc, exit)
    cli.alias(session, "quit", "exit $*")
    cli.register('stop', _stop_desc, stop)
    cli.register('echo', _echo_desc, echo)
    cli.register('pwd', _pwd_desc, pwd)
    # def lighting_cmds():
    #     import .lighting.cmd as cmd
    #     cmd.register()
    # cli.delay_registration('lighting', lighting_cmds)
