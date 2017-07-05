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

#ifndef atomstruct_Residue
#define atomstruct_Residue

#include <map>
#include <set>
#include <string>
#include <vector>

#include "backbone.h"
#include "imex.h"
#include "session.h"
#include "string_types.h"
#include "ChangeTracker.h"
#include "Real.h"
#include "Rgba.h"

namespace atomstruct {

class Atom;
class Bond;
class Chain;
class Structure;

class ATOMSTRUCT_IMEX Residue {
public:
    typedef std::vector<Atom *>  Atoms;
    typedef std::multimap<AtomName, Atom *>  AtomsMap;
    enum PolymerType { PT_NONE = 0, PT_AMINO = 1, PT_NUCLEIC = 2 };
    enum SSType { SS_COIL = 0, SS_HELIX = 1, SS_STRAND = 2 };
    static constexpr Real TRACE_DISTSQ_CUTOFF = 45.0;
private:
    friend class Structure;
    Residue(Structure *as, const ResName& name, const ChainID& chain, int pos, char insert);
    virtual  ~Residue();

    friend class StructureSeq;
    void  set_chain(Chain* chain) {
        _chain = chain;
        if (chain == nullptr) set_ribbon_display(false);
    }
    friend class AtomicStructure;
    friend class Bond;
    void  set_polymer_type(PolymerType pt) { _polymer_type = pt; }

    static int  SESSION_NUM_INTS(int version=CURRENT_SESSION_VERSION) { return version < 6 ? 10 : 9; }
    static int  SESSION_NUM_FLOATS(int /*version*/=CURRENT_SESSION_VERSION) { return 1; }

    char  _alt_loc;
    Atoms  _atoms;
    Chain*  _chain;
    ChainID  _chain_id;
    char  _insertion_code;
    bool  _is_het;
    ChainID  _mmcif_chain_id;
    ResName  _name;
    PolymerType  _polymer_type;
    int  _number;
    float  _ribbon_adjust;
    bool  _ribbon_display;
    bool  _ribbon_hide_backbone;
    Rgba  _ribbon_rgba;
    bool  _ribbon_selected = false;
    int  _ss_id;
    SSType _ss_type;
    Structure *  _structure;
public:
    void  add_atom(Atom*);
    const Atoms&  atoms() const { return _atoms; }
    AtomsMap  atoms_map() const;
    std::vector<Bond*>  bonds_between(const Residue* other_res, bool just_first=false) const;
    Chain*  chain() const;
    const ChainID&  chain_id() const;
    bool  connects_to(const Residue* other_res) { return !bonds_between(other_res, true).empty(); }
    int  count_atom(const AtomName&) const;
    Atom *  find_atom(const AtomName&) const;
    const ChainID&  mmcif_chain_id() const { return _mmcif_chain_id; }
    char  insertion_code() const { return _insertion_code; }
    bool  is_helix() const { return ss_type() == SS_HELIX; }
    bool  is_het() const { return _is_het; }
    bool  is_strand() const { return ss_type() == SS_STRAND; }
    const ResName&  name() const { return _name; }
    PolymerType  polymer_type() const { return _polymer_type; }
    int  number() const { return _number; }
    Atom*  principal_atom() const;
    void  remove_atom(Atom*);
    int  session_num_floats(int version=CURRENT_SESSION_VERSION) const {
        return SESSION_NUM_FLOATS(version) + Rgba::session_num_floats();
    }
    int  session_num_ints(int version=CURRENT_SESSION_VERSION) const {
        return SESSION_NUM_INTS(version) + Rgba::session_num_ints() + atoms().size();
    }
    void  session_restore(int, int**, float**);
    void  session_save(int**, float**) const;
    void  set_alt_loc(char alt_loc);
    void  set_mmcif_chain_id(const ChainID &cid) { _mmcif_chain_id = cid; }
    void  set_insertion_code(char ic) { _insertion_code = ic; }
    void  set_is_helix(bool ih);
    void  set_is_het(bool ih);
    void  set_is_strand(bool is);
    void  set_ss_id(int ssid);
    void  set_ss_type(SSType sst);
    int  ss_id() const {
        if (!structure()->ss_assigned())
            structure()->compute_secondary_structure();
        return _ss_id;
    }
    SSType  ss_type() const {
        if (!structure()->ss_assigned())
            structure()->compute_secondary_structure();
        return _ss_type;
    }
    std::string  str() const;
    Structure*  structure() const { return _structure; }
    std::vector<Atom*>  template_assign(
        void (Atom::*assign_func)(const char*), const char* app,
        const char* template_dir, const char* extension) const;

    // handy
    static const std::set<AtomName>  aa_min_backbone_names;
    static const std::set<AtomName>  aa_max_backbone_names;
    static const std::set<AtomName>  aa_ribbon_backbone_names;
    static const std::set<AtomName>  na_min_backbone_names;
    static const std::set<AtomName>  na_max_backbone_names;
    static const std::set<AtomName>  na_ribbon_backbone_names;
    static const std::set<AtomName>  ribose_names;
    static const std::set<ResName>  std_solvent_names;
    const std::set<AtomName>*  backbone_atom_names(BackboneExtent bbe) const;
    const std::set<AtomName>*  ribose_atom_names() const;

    // graphics related
    float  ribbon_adjust() const;
    const Rgba&  ribbon_color() const { return _ribbon_rgba; }
    bool  ribbon_display() const { return _ribbon_display; }
    bool  ribbon_hide_backbone() const { return _ribbon_hide_backbone; }
    bool  ribbon_selected() const { return _ribbon_selected; }
    void  set_ribbon_adjust(float a);
    void  set_ribbon_color(const Rgba& rgba);
    void  set_ribbon_display(bool d);
    void  set_ribbon_hide_backbone(bool d);
    void  set_ribbon_selected(bool s);
    void  ribbon_clear_hide();
};

}  // namespace atomstruct

#include "Structure.h"
#include "Chain.h"

namespace atomstruct {

inline const std::set<AtomName>*
Residue::backbone_atom_names(BackboneExtent bbe) const
{
    if (!structure()->_polymers_computed) structure()->polymers();
    if (polymer_type() == PT_AMINO) {
        if (bbe == BBE_RIBBON) return &aa_ribbon_backbone_names;
        if (bbe == BBE_MAX) return &aa_max_backbone_names;
        return &aa_min_backbone_names;
    }
    if (polymer_type() == PT_NUCLEIC) {
        if (bbe == BBE_RIBBON) return &na_ribbon_backbone_names;
        if (bbe == BBE_MAX) return &na_max_backbone_names;
        return &na_min_backbone_names;
    }
    return nullptr;
}

inline const ChainID&
Residue::chain_id() const
{
    if (_chain != nullptr)
        return _chain->chain_id();
    return _chain_id;
}

inline Chain*
Residue::chain() const {
    (void)_structure->chains();
    return _chain;
}

inline float
Residue::ribbon_adjust() const {
    if (_ribbon_adjust >= 0)
        return _ribbon_adjust;
    else if (_ss_type == SS_STRAND)
        return 1.0;
    else if (_ss_type == SS_HELIX)
        return 0.0;
    else
        return 0.0;
}

inline const std::set<AtomName>*
Residue::ribose_atom_names() const
{
    if (!structure()->_polymers_computed) structure()->polymers();
    if (polymer_type() == PT_NUCLEIC)
        return &ribose_names;
    return nullptr;
}

inline void
Residue::set_is_helix(bool ih) {
    // old implementation had two booleans for is_helix and is_strand;
    // now sets the ss_type instead
    if (ih)
        set_ss_type(SS_HELIX);
    else
        set_ss_type(SS_COIL);
}

inline void
Residue::set_is_het(bool ih) {
    if (ih == _is_het)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_IS_HET);
    _is_het = ih;
}

inline void
Residue::set_is_strand(bool is) {
    // old implementation had two booleans for is_helix and is_strand;
    // now sets the ss_type instead
    if (is)
        set_ss_type(SS_STRAND);
    else
        set_ss_type(SS_COIL);
}

inline void
Residue::set_ribbon_adjust(float a) {
    if (a == _ribbon_adjust)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_RIBBON_ADJUST);
    _structure->set_gc_ribbon();
    _ribbon_adjust = a;
}

inline void
Residue::set_ribbon_color(const Rgba& rgba) {
    if (rgba == _ribbon_rgba)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_RIBBON_COLOR);
    _structure->set_gc_ribbon();
    _ribbon_rgba = rgba;
}

inline void
Residue::set_ribbon_display(bool d) {
    if (d == _ribbon_display)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_RIBBON_DISPLAY);
    _structure->set_gc_ribbon();
    _ribbon_display = d;
    if (d)
        _structure->_ribbon_display_count += 1;
    else {
        _structure->_ribbon_display_count -= 1;
        ribbon_clear_hide();
    }
}

inline void
Residue::set_ribbon_hide_backbone(bool d) {
    if (d == _ribbon_hide_backbone)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_RIBBON_HIDE_BACKBONE);
    _structure->set_gc_ribbon();
    _ribbon_hide_backbone = d;
}

inline void
Residue::set_ss_id(int ss_id)
{
    if (ss_id == _ss_id)
        return;
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_SS_ID);
    _ss_id = ss_id;
    _structure->set_gc_ribbon();
}

inline void
Residue::set_ss_type(SSType sst)
{
    if (sst == _ss_type)
        return;
    _structure->set_ss_assigned(true);
    _structure->change_tracker()->add_modified(this, ChangeTracker::REASON_SS_TYPE);
    _ss_type = sst;
    _structure->set_gc_ribbon();
}

}  // namespace atomstruct

#include "Atom.h"
#include "Bond.h"

namespace atomstruct {
    
inline void
Residue::ribbon_clear_hide() {
    for (auto atom: atoms()) {
        atom->set_hide(atom->hide() & ~Atom::HIDE_RIBBON);
        for (auto bond: atom->bonds())
            bond->set_hide(bond->hide() & ~Bond::HIDE_RIBBON);
    }
}

}  // namespace atomstruct

#endif  // atomstruct_Residue
