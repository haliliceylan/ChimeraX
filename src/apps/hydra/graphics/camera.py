'''
Camera
======
'''

class Camera:
    '''
    A Camera has a position in the scene and viewing direction given by a Place object.
    The -z axis of the coordinate frame given by the Place object is the view direction.
    The x and y axes are the horizontal and vertical axes of the camera frame.
    A camera has an angular field of view measured in degrees. In stereo modes it uses
    two additional parameters, the eye spacing
    in scene units, and also the eye spacing in pixels in the window.  The two eyes
    are considered 2 views that belong to one camera.
    '''
    def __init__(self):

        # Camera postion and direction, neg z-axis is camera view direction,
        # x and y axes are horizontal and vertical screen axes.
        # First 3 columns are x,y,z axes, 4th column is camara location.
        from ..geometry.place import Place
        self._position = Place()
        "Coordinate frame for camera in scene coordinates with camera pointed along -z."

        self.field_of_view = 45
        "Horizontal field of view in degrees."

        self._mode = mono_camera_mode    # CameraMode for mono, stereo, oculus... rendering

        self.pixel_shift = 0,0
        '''
        Shift the camera by this number of pixels in x and y from the geometric center of the window.
        This is used for supersampling where fractional pixel shifts are used and the resulting images
        are blended.
        '''

        self.redraw_needed = False
        "Indicates whether a camera change has been made which requires the graphics to be redrawn."

    def get_mode(self):
        return self._mode
    def set_mode(self, mode):
        self._mode = mode
        self.redraw_needed = True
    mode = property(get_mode, set_mode)
    '''Set the camera mode to a CameraMode object.'''

    def get_position(self, view_num = None):
        p = self._position if view_num is None else self.mode.view(self._position, view_num)
        return p
    def set_position(self, p):
        self._position = p
        self.redraw_needed = True
    position = property(get_position, set_position)
    '''Location and orientation of the camera in scene coordinates. Camera points along -z axis.'''

    def initialize_view(self, center, size):
        '''
        Set the camera to completely show models having specified center and radius
        looking along the scene -z axis.
        '''
        cx,cy,cz = center
        from math import pi, tan
        fov = self.field_of_view*pi/180
        camdist = 0.5*size + 0.5*size/tan(0.5*fov)
        from ..geometry import place
        self.position = place.translation((cx,cy,cz+camdist))

    def view_all(self, center, size):
        '''
        Return the shift that makes the camera completely show models having specified center and radius.
        The camera view direction is not changed.
        '''
        from math import pi, tan
        fov = self.field_of_view*pi/180
        d = 0.5*size + 0.5*size/tan(0.5*fov)
        vd = self.view_direction()
        cp = self.position.origin()
        from numpy import array, float32
        shift = array(tuple((center[a]-d*vd[a])-cp[a] for a in (0,1,2)), float32)
        return shift

    def view_width(self, center):
        '''Return the width of the view at position center which is in scene coordinates.'''
        cp = self.position.origin()
        vd = self.view_direction()
        d = sum((center-cp)*vd)         # camera to center of models
        from math import tan, pi
        vw = 2*d*tan(0.5*self.field_of_view*pi/180)     # view width at center
        return vw

    def pixel_size(self, center, window_size):
        '''
        Return the size of a pixel in scene units for a point at position center.
        Center is given in scene coordinates and perspective projection is accounted for.
        '''
        # Pixel size at center
        w,h = window_size
        from math import pi, tan
        fov = self.field_of_view * pi/180

        c = self.position.origin()
        from ..geometry import vector
        ps = vector.distance(c,center) * 2*tan(0.5*fov) / w
        return ps

    def view_direction(self, view_num = None):
        '''The view direction of the camera in scene coordinates.'''
        return -self.get_position(view_num).z_axis()

    def projection_matrix(self, near_far_clip, view_num, window_size):
        '''The 4 by 4 OpenGL perspective projection matrix for rendering the scene using this camera view.'''
        # Perspective projection to origin with center of view along z axis
        from math import pi, tan
        fov = self.field_of_view*pi/180
        near,far = near_far_clip
        w = 2*near*tan(0.5*fov)
        ww,wh = window_size
        aspect = wh/ww
        h = w*aspect
        left, right, bot, top = -0.5*w, 0.5*w, -0.5*h, 0.5*h
        xps,yps = self.pixel_shift
        mxs,mys = self.mode.pixel_shift(view_num)
        xshift,yshift = (xps+mxs)/ww, (yps+mys)/wh
        pm = frustum(left, right, bot, top, near, far, xshift, yshift)
        return pm

    def clip_plane_points(self, window_x, window_y, window_size, z_distances, render):
        '''
        Return two scene points at the near and far clip planes at the specified window pixel position.
        TODO: Only correct for mono camera.
        '''
        from math import pi, tan
        fov = self.field_of_view*pi/180
        t = tan(0.5*fov)
        wp,hp = window_size     # Screen size in pixels
        wx,wy = (window_x - 0.5*wp)/wp, (0.5*hp - window_y)/wp
        cpts = []
        for z in z_distances:
            w = 2*z*t   # Render width in scene units
            c = (w*wx, w*wy, -z)
            cpts.append(c)
        view_num = 0
        spts = self.get_position(view_num) * cpts       # Convert camera to scene coordinates
        return spts

    def number_of_views(self):
        '''Number of view points for this camera.  Stereo modes have 2 views for left and right eyes.'''
        return self.mode.number_of_views()

    def set_render_target(self, view_num, render):
        '''Set the OpenGL drawing buffer and viewport to render the scene.'''
        self.mode.set_render_target(view_num, render)

    def combine_rendered_camera_views(self, render):
        '''Combine camera views into a single image.'''
        self.mode.combine_rendered_camera_views(render)

class CameraMode:

    def name(self):
        '''Name of camera mode.'''
        return 'mono'

    def view(self, camera_position, view_num):
        '''
        Return the Place coordinate frame of the camera.
        As a transform it maps camera coordinates to scene coordinates.
        '''
        return camera_position

    def number_of_views(self):
        '''Number of views rendered by camera mode.'''
        return 1

    def pixel_shift(self, view_num):
        '''Shift of center away from center of render target.'''
        return 0,0

    def set_render_target(self, view_num, render):
        '''Set the OpenGL drawing buffer and viewport to render the scene.'''
        render.set_mono_buffer()

    def combine_rendered_camera_views(self, render):
        '''Combine camera views into a single image.'''
        return

    def do_swap_buffers(self):
        return True

mono_camera_mode = CameraMode()

class StereoCameraMode(CameraMode):
    '''Sequential stereo camera mode.'''

    def __init__(self, eye_separation_pixels = 200):
        self.eye_separation_scene = 1.0
        "Stereo eye separation in scene units."

        self.eye_separation_pixels = eye_separation_pixels
        "Separation of the user's eyes in screen pixels used for stereo rendering."

    def name(self):
        return 'stereo'

    def view(self, camera_position, view_num):
        '''
        Return the Place coordinate frame of the camera.
        As a transform it maps camera coordinates to scene coordinates.
        '''
        if view_num is None:
            v = camera_position
        else:
            # Stereo eyes view in same direction with position shifted along x.
            s = -1 if view_num == 0 else 1
            es = self.eye_separation_scene
            from ..geometry import place
            t = place.translation((s*0.5*es,0,0))
            v = camera_position * t
        return v

    def number_of_views(self):
        '''Number of views rendered by camera mode.'''
        return 2

    def pixel_shift(self, view_num):
        '''Shift of center away from center of render target.'''
        if view_num is None:
            return 0,0
        s = -1 if view_num == 0 else 1
        return (s*0.5*self.eye_separation_pixels, 0)

    def set_render_target(self, view_num, render):
        '''Set the OpenGL drawing buffer and viewport to render the scene.'''
        render.set_stereo_buffer(view_num)

stereo_camera_mode = StereoCameraMode()

# glFrustum() matrix
def frustum(left, right, bottom, top, zNear, zFar, xshift = 0, yshift = 0):
    '''
    Return a 4 by 4 perspective projection matrix.  It includes a shift along x used
    to superpose offset left and right eye views in sequential stereo mode.
    '''
    A = (right + left) / (right - left) - 2*xshift
    B = (top + bottom) / (top - bottom) - 2*yshift
    C = - (zFar + zNear) / (zFar - zNear)
    D = - (2 * zFar * zNear) / (zFar - zNear)
    E = 2 * zNear / (right - left)
    F = 2 * zNear / (top - bottom)
    m = ((E, 0, 0, 0),
         (0, F, 0, 0),
         (A, B, C, -1),
         (0, 0, D, 0))
    return m

def camera_framing_models(models):
    '''
    Create a Camera object for viewing the specified models.
    This is used for capturing thumbnail images.
    '''
    c = Camera()
    from ..geometry import bounds
    b = bounds.union_bounds(m.bounds() for m in models)
    if b is None:
        return None
    c.initialize_view(b.center(), b.width())
    return c
