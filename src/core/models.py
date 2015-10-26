# vi: set expandtab shiftwidth=4 softtabstop=4:
"""
models: Displayed data
======================

"""

import weakref
from .graphics.drawing import Drawing
from .session import State, RestoreError
ADD_MODELS = 'add models'
REMOVE_MODELS = 'remove models'
# TODO: register Model as data event type


class Model(State, Drawing):
    """A Model is a :class:`.Drawing` together with an id number 
    that allows it to be referenced in a typed command.

    Model subclasses can be saved session files.

    Parameters
    ----------
    name : str
        The name of the model.

    Attributes
    ----------
    id : None or tuple of int
        Model/submodel identification: *e.g.*, 1.3.2 is (1, 3, 2).
        Set and unset by :py:class:`Models` instance.
    tool_info : a :py:class:`~chimera.core.toolshed.ToolInfo` instance
        The tool that provides the subclass.
    SESSION_ENDURING : bool, class-level optional
        If True, then model survives across sessions.
    SESSION_SKIP : bool, class-level optional
        If True, then model is not saved in sessions.
    """

    MODEL_STATE_VERSION = 1
    SESSION_ENDURING = False
    SESSION_SKIP = False
    tool_info = None    # default, should be set in subclass

    def __init__(self, name):
        Drawing.__init__(self, name)
        self.id = None
        # TODO: track.created(Model, [self])

    def delete(self):
        Drawing.delete(self)

    def id_string(self):
        return '.'.join(str(i) for i in self.id)

    def add(self, models):
        for m in models:
            self.add_drawing(m)

    def child_models(self):
        '''Return all models including self and children at all levels.'''
        return [d for d in self.child_drawings() if isinstance(d, Model)]

    def all_models(self):
        '''Return all models including self and children at all levels.'''
        dlist = [self]
        for d in self.child_drawings():
            if isinstance(d, Model):
                dlist.extend(d.all_models())
        return dlist

    def take_snapshot(self, phase, session, flags):
        if phase != self.SAVE_PHASE:
            return
        return [self.MODEL_STATE_VERSION, self.name]

    def restore_snapshot(self, phase, session, version, data):
        if phase != self.CREATE_PHASE:
            return
        if version != self.MODEL_STATE_VERSION:
            raise RestoreError("Unexpected version")
        self.name = data

    def reset_state(self):
        pass

    def selected_items(self, itype):
        return []

    def added_to_session(self, session):
        pass

    def removed_from_session(self, session):
        pass

class Models(State):

    VERSION = 1     # snapshot version

    def __init__(self, session):
        self._session = weakref.ref(session)
        session.triggers.add_trigger(ADD_MODELS)
        session.triggers.add_trigger(REMOVE_MODELS)
        self._models = {}
        from .graphics.drawing import Drawing
        self.drawing = r = Model("root")
        r.id = ()

    def take_snapshot(self, phase, session, flags):
        if phase == self.CLEANUP_PHASE:
            for model in self._models.values():
                if model.SESSION_SKIP:
                    continue
                model.take_snapshot(session, phase, flags)
            return
        if phase != self.SAVE_PHASE:
            return
        data = {}
        for id, model in self._models.items():
            assert(isinstance(model, Model))
            if model.SESSION_SKIP:
                continue
            data[id] = [session.unique_id(model),
                        model.take_snapshot(session, phase, flags)]
        return [self.VERSION, data]

    def restore_snapshot(self, phase, session, version, data):
        if version != self.VERSION:
            raise RestoreError("Unexpected version")

        for id, [uid, [model_version, model_data]] in data.items():
            if phase == self.CREATE_PHASE:
                print('restoring1', uid)
                try:
                    cls = session.class_of_unique_id(uid, Model)
                except KeyError:
                    session.log.warning(
                        'Unable to restore model %s (%s)'
                        % (id, session.class_name_of_unique_id(uid)))
                    continue
                model = cls("unknown name until restored")
                model.id = id
                self._models[id] = model
                session.restore_unique_id(model, uid)
            else:
                model = session.unique_obj(uid)
                if len(model.id) == 1:
                    parent = self.drawing
                else:
                    parent = self._models[model.id[:-1]]
                parent.add_drawing(model)
            model.restore_snapshot(phase, session, model_version, model_data)

    def reset_state(self):
        models = self._models.values()
        self._models.clear()
        for model in models:
            if model.SESSION_ENDURING:
                continue
            model.delete()

    def list(self, model_id=None, type=None):
        if model_id is None:
            models = list(self._models.values())
        else:
            if model_id not in self._models:
                return []
            # find all submodels
            size = len(model_id)
            model_ids = [x for x in self._models if x[0:size] == model_id]
            # sort so submodels are removed before parent models
            model_ids.sort(key=len, reverse=True)
            models = [self._models[x] for x in model_ids]
        if not type is None:
            models = [m for m in models if isinstance(m,type)]
        return models

    def add(self, models, parent=None, _notify=True):
        d = self.drawing if parent is None else parent
        for m in models:
            d.add_drawing(m)

        # Assign id numbers
        m_all = list(models)
        for model in models:
            if model.id is None:
                model.id = self._next_child_id(d)
            self._models[model.id] = model
            children = [c for c in model.child_drawings() if isinstance(c, Model)]
            if children:
                m_all.extend(self.add(children, model, _notify=False))

        if _notify:
            session = self._session()
            for m in m_all:
                m.added_to_session(session)
            session.triggers.activate_trigger(ADD_MODELS, m_all)

        return m_all

    def _next_child_id(self, parent):
        # Find lowest unused id.  Typically all ids 1,...,N are used with no gaps
        # and then it is fast to assign N+1 to the next model.  But if there are
        # gaps it can take O(N**2) time to figure out ids to assign for N models.
        # This code handles the common case of no gaps quickly.
        nid = getattr(parent, '_next_unused_id', None)
        if nid is None:
            # Find next unused id.
            cids = set(m.id[-1] for m in parent.child_models() if not m.id is None)
            for nid in range(1,len(cids)+2):
                if not nid in cids:
                    break
            if nid == len(cids)+1:
                parent._next_unused_id = nid + 1	# No gaps in ids
        else:
            parent._next_unused_id = nid + 1		# No gaps in ids
        id = parent.id + (nid,)
        return id

    def add_group(self, models, name='group'):
        parent = Model(name)
        parent.add(models)
        m_all = self.add([parent])
        return [parent] + m_all

    def remove(self, models):
        # Also remove all child models, and remove deepest children first.
        mlist = descendant_models(models)
        mlist.sort(key=lambda m: len(m.id), reverse=True)
        session = self._session()  # resolve back reference
        for m in mlist:
            m.removed_from_session(session)
        for model in mlist:
            model_id = model.id
            if model_id is not None:
                del self._models[model_id]
                model.id = None
                if len(model_id) == 1:
                    parent = self.drawing
                else:
                    parent = self._models[model_id[:-1]]
                parent.remove_drawing(model, delete = False)
                parent._next_unused_id = None

        # it's nice to have an accurate list of current models
        # when firing this trigger, so do it last
        session.triggers.activate_trigger(REMOVE_MODELS, mlist)

    def close(self, models):
        self.remove(models)
        for m in models:
            m.delete()

    def open(self, filenames, id=None, **kw):
        from . import io
        session = self._session()  # resolve back reference
        models, status = io.open_multiple_data(session, filenames, **kw)
        if status:
            session.logger.status(status)
        if models:
            start_count = len(self._models)
            if len(models) > 1:
                self.add_group(models)
            else:
                self.add(models)
            if start_count == 0 and len(self._models) > 0:
                session.main_view.initial_camera_view()
        return models


def descendant_models(models):
    mset = set()
    for m in models:
        mset.update(m.all_models())
    return list(mset)
