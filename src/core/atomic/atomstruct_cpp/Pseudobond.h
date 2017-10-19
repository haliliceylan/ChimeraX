// vi: set expandtab ts=4 sw=4:

/*
 * === UCSF ChimeraX Copyright ===
 * Copyright 2016 Regents of the University of California.
 * All rights reserved.  This software provided pursuant to a
 * license agreement containing restrictions on its disclosure,
 * duplication and use.  For details see:
 * http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html
 * This notice must be embedded in or attached to all copies,
 * including partial copies, of the software or any revisions
 * or derivations thereof.
 * === UCSF ChimeraX Copyright ===
 */

#ifndef atomstruct_Pseudobond
#define atomstruct_Pseudobond

#include "Connection.h"
#include "imex.h"
#include "PythonInstance.h"
#include "session.h"

// "forward declare" PyObject, which is a typedef of a struct,
// as per the python mailing list:
// http://mail.python.org/pipermail/python-dev/2003-August/037601.html
#ifndef PyObject_HEAD
struct _object;
typedef _object PyObject;
#endif
    
namespace atomstruct {

class Atom;
class ChangeTracker;
class GraphicsChanges;
class PBGroup;

class ATOMSTRUCT_IMEX Pseudobond: public Connection, public PythonInstance
{
public:
    friend class PBGroup;
    friend class StructurePBGroup;
    friend class CS_PBGroup;

protected:
    PBGroup*  _group;
    bool  _shown_when_atoms_hidden;

    Pseudobond(Atom* a1, Atom* a2, PBGroup* grp): Connection(a1, a2), _group(grp),
            _shown_when_atoms_hidden(true) { _halfbond = false; _radius = 0.05;
    }
    virtual ~Pseudobond() { graphics_changes()->set_gc_adddel(); }

    // convert a global pb_manager version# to version# for Connection base class
    static int  SESSION_NUM_INTS(int version=CURRENT_SESSION_VERSION) { return version<9 ? 1 : 2; }
    static int  SESSION_NUM_FLOATS(int /*version*/=CURRENT_SESSION_VERSION) { return 0; }
    const char*  err_msg_loop() const
        { return "Can't form pseudobond to itself"; }
    const char*  err_msg_not_end() const
        { return "Atom given to other_end() not in pseudobond!"; }
public:
    ChangeTracker*  change_tracker() const;
    GraphicsChanges*  graphics_changes() const;
    PBGroup*  group() const { return _group; }
    void  set_shown_when_atoms_hidden(bool s) { _shown_when_atoms_hidden = s; }
    bool  shown() const
    { return (visible() && (_shown_when_atoms_hidden ?
        ((atoms()[0]->display() || atoms()[0]->hide()) &&
        (atoms()[1]->display() || atoms()[1]->hide()))
        :
        ((atoms()[0]->display() && !atoms()[0]->hide()) &&
        (atoms()[1]->display() && !atoms()[1]->hide())))); }
    bool  shown_when_atoms_hidden() const { return _shown_when_atoms_hidden; }
    static int  session_num_floats(int version=CURRENT_SESSION_VERSION) {
        return SESSION_NUM_FLOATS(version) + Connection::session_num_floats(version);
    }
    static int  session_num_ints(int version=CURRENT_SESSION_VERSION) {
        return SESSION_NUM_INTS(version) + Connection::session_num_ints(version);
    }
    void  session_restore(int version, int** ints, float** floats);
    void  session_save(int** ints, float** floats) const;
    void  track_change(const std::string& reason) const {
        change_tracker()->add_modified(this, reason);
    }
};

}  // namespace atomstruct

#include "PBGroup.h"

namespace atomstruct {

class CoordSet;

class ATOMSTRUCT_IMEX CS_Pseudobond: public Pseudobond
{
public:
    friend class CS_PBGroup;

private:
    CoordSet*  _cs;

    CS_Pseudobond(Atom* a1, Atom* a2, CS_PBGroup* grp, CoordSet* cs):
        Pseudobond(a1, a2, static_cast<PBGroup*>(grp)), _cs(cs) {}

public:
    CoordSet*  coord_set() const { return _cs; }

};

}  // namespace atomstruct

#endif  // atomstruct_Pseudobond
