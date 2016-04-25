def rainbow(session, objects, level='residues', target=None, transparency=None,
            palette=None, halfbond=None):
    '''
    Color residues or chains by sequence using a color map.
    Arguments are the same as for the color command.
    '''
    from .color import color
    color(session, objects, target=target, transparency=transparency,
          sequential=level, palette=palette, halfbond=halfbond)

# -----------------------------------------------------------------------------
#
def register_command(session):
    from . import register, CmdDesc, ColormapArg, ObjectsArg
    from . import EmptyArg, Or, EnumOf, StringArg, TupleOf, FloatArg, BoolArg
    from .color import _SequentialLevels
    desc = CmdDesc(required=[('objects', Or(ObjectsArg, EmptyArg))],
                   optional=[('level', EnumOf(_SequentialLevels))],
                   keyword=[('target', StringArg),
                            ('transparency', FloatArg),
                            ('palette', ColormapArg),
                            ('halfbond', BoolArg)],
                   url='help:user/commands/color.html#rainbow',
                   synopsis="color residues and chains sequentially")
    register('rainbow', desc, rainbow)
