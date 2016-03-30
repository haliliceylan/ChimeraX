// vi: set expandtab ts=4 sw=4:
#ifndef atomstruct_Bond
#define atomstruct_Bond

#include <set>
#include <vector>

#include "Connection.h"
#include "imex.h"

namespace atomstruct {

class Atom;
class ChangeTracker;
class Structure;
class Residue;
class Ring;

class ATOMSTRUCT_IMEX Bond: public UniqueConnection {
    friend class Structure;
public:
    // HIDE_ constants are masks for hide bits in Atom
    static const unsigned int  HIDE_RIBBON = 0x1;
    typedef std::vector<const Ring*>  Rings;
private:
    Bond(Structure*, Atom*, Atom*);
    void  add_to_atoms() { atoms()[0]->add_bond(this); atoms()[1]->add_bond(this); }
    const char*  err_msg_exists() const
        { return "Bond already exists between these atoms"; }
    const char*  err_msg_loop() const
        { return "Can't bond an atom to itself"; }
    mutable Rings  _rings;

    static int  session_base_version(int /*version*/) { return 1; }
    static int  SESSION_NUM_INTS(int /*version*/=0) { return 0; }
    static int  SESSION_NUM_FLOATS(int /*version*/=0) { return 0; }
public:
    virtual ~Bond() {}
    virtual bool shown() const;
    const Rings&  all_rings(bool cross_residues = false, int size_threshold = 0,
        std::set<const Residue*>* ignore = nullptr) const;
    Structure*  structure() const;
    // length() inherited from UniqueConnection
    const Rings&  minimum_rings(bool cross_residues = false,
            std::set<const Residue*>* ignore = nullptr) const {
        return rings(cross_residues, 0, ignore);
    }
    static bool  polymer_bond_atoms(Atom* first, Atom* second);
    Atom*  polymeric_start_atom() const;
    const Rings&  rings(bool cross_residues = false, int all_size_threshold = 0,
        std::set<const Residue*>* ignore = nullptr) const;
    // sqlength() inherited from UniqueConnection

    // session related
    static int  session_num_floats(int version=0) {
        return SESSION_NUM_FLOATS(version)
            + UniqueConnection::session_num_floats(session_base_version(version));
    }
    static int  session_num_ints(int version=0) {
        return SESSION_NUM_INTS(version)
            + UniqueConnection::session_num_ints(session_base_version(version));
    }
    // session_restore and session_save simply inherited from UniqueConnection

    // change tracking
    ChangeTracker*  change_tracker() const;
    void track_change(const std::string& reason) const {
        change_tracker()->add_modified(this, reason);
    }

    // graphics related
    GraphicsContainer*  graphics_container() const;
};

}  // namespace atomstruct

#include "Atom.h"
#include "Structure.h"

namespace atomstruct {

inline bool Bond::shown() const {
    return Connection::shown() &&
      (atoms()[0]->draw_mode() != Atom::DrawMode::Sphere ||
       atoms()[0]->draw_mode() != Atom::DrawMode::Sphere);
}

inline ChangeTracker*
Bond::change_tracker() const { return atoms()[0]->change_tracker(); }

inline const Bond::Rings&
Bond::all_rings(bool cross_residues, int size_threshold,
    std::set<const Residue*>* ignore) const
{
    int max_ring_size = size_threshold;
    if (max_ring_size == 0)
        max_ring_size = atoms()[0]->structure()->num_atoms();
    return rings(cross_residues, max_ring_size, ignore);
}

inline GraphicsContainer*
Bond::graphics_container() const {
    return reinterpret_cast<GraphicsContainer*>(atoms()[0]->structure());
}

inline const Bond::Rings&
Bond::rings(bool cross_residues, int all_size_threshold,
    std::set<const Residue*>* ignore) const
{
    atoms()[0]->structure()->rings(cross_residues, all_size_threshold, ignore);
    return _rings;
}

inline Structure* Bond::structure() const { return atoms()[0]->structure(); }

}  // namespace atomstruct

#endif  // atomstruct_Bond
