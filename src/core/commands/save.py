# vim: set expandtab shiftwidth=4 softtabstop=4:


def save(session, filename, width=None, height=None, supersample=None,
         transparent_background=False, quality=95, format=None):
    '''Save data, sessions, images.

    Parameters
    ----------
    filename : string
        File to save.
        File suffix determines what type of file is saved unless
        the format option is given.
        For sessions the suffix is .cxses.
        Image files can be saved with .png, .jpg, .tif, .ppm, .gif suffixes.
    width : integer
        Width of image in pixels for saving image files.
        If width is not specified the current graphics window width is used.
    height : integer
        Height of image in pixels for saving image files.
    supersample : integer
        Supersampling for saving images.
        Makes an image N times larger in each dimension
        then averages to requested image size to produce smoother object edges.
        Values of 2 or 3 are most useful,
        with little improvement for larger values.
    transparent_background : bool
        Save image with transparent background.
    format : string
        File format for saving images.
        If not specified,
        then the filename suffix is used to identify the format.
    '''
    from .. import session as ses
    ses_suffix = ses.SESSION_SUFFIX[1:]
    from os.path import splitext
    suffix = splitext(filename)[1][1:].casefold()
    if not suffix and format:
        suffix = format
        filename += '.%s' % suffix
    if suffix in image_file_suffixes:
        save_image(session, filename, format, width, height,
                   supersample, transparent_background, quality)
    elif suffix == ses_suffix:
        ses.save(session, filename)
    else:
        suffixes = image_file_suffixes + (ses_suffix,)
        from ..errors import UserError
        from . import commas
        tokens = commas(["'%s'" % i for i in suffixes])
        if not suffix:
            raise UserError('Missing file suffix, require one of %s' % tokens)
        raise UserError('Unrecognized file suffix "%s", require one of %s' %
                        (suffix, tokens))


def register_command(session):
    from . import CmdDesc, register, EnumOf, StringArg, IntArg, BoolArg, PositiveIntArg, Bounded
    from .. import session as ses
    ses_suffix = ses.SESSION_SUFFIX[1:]
    img_fmts = EnumOf(image_formats.keys())
    all_fmts = EnumOf(tuple(image_formats.keys()) + (ses_suffix,))
    quality_arg = Bounded(IntArg, min=0, max=100)
    desc = CmdDesc(
        required=[('filename', StringArg), ],
        keyword=[
            ('width', PositiveIntArg),
            ('height', PositiveIntArg),
            ('supersample', PositiveIntArg),
            ('transparent_background', BoolArg),
            ('quality', quality_arg),
            ('format', all_fmts),
        ],
        synopsis='save session or image'
    )
    register('save', desc, save)

    desc = CmdDesc(
        required=[('filename', StringArg), ],
        # synopsis='save session'
    )
    from .. import session as ses
    register('save session', desc, ses.save)

    desc = CmdDesc(
        required=[('filename', StringArg), ],
        keyword=[
            ('width', PositiveIntArg),
            ('height', PositiveIntArg),
            ('supersample', PositiveIntArg),
            ('transparent_background', BoolArg),
            ('quality', quality_arg),
            ('format', img_fmts),
        ],
        # synopsis='save image'
    )
    register('save image', desc, save_image)

# Table mapping file suffix to Pillow image format.
image_formats = {
    'png': 'PNG',
    'jpg': 'JPEG',
    'tif': 'TIFF',
    'gif': 'GIF',
    'ppm': 'PPM',
    'bmp': 'BMP',
}
image_file_suffixes = tuple(image_formats.keys())


def save_image(session, filename, format=None, width=None, height=None,
               supersample=None, transparent_background=False, quality=95):
    '''
    Save an image of the current graphics window contents.
    '''
    from os.path import expanduser, dirname, exists, splitext
    path = expanduser(filename)         # Tilde expansion
    dir = dirname(path)
    if dir and not exists(dir):
        from ..errors import UserError
        raise UserError('Directory "%s" does not exist' % dir)

    if format is None:
        suffix = splitext(path)[1][1:].casefold()
        if suffix not in image_file_suffixes:
            raise UserError('Unrecognized image file suffix "%s"' % format)
        format = image_formats[suffix]

    view = session.main_view
    i = view.image(width, height, supersample=supersample,
                   transparent_background=transparent_background)
    i.save(path, image_formats[format], quality=quality)
