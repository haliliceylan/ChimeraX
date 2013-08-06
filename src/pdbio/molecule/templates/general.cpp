#include "resinternal.h"


static TmplResidue *
init_TIP3(TmplMolecule *m)
{
	TmplCoord c;
	TmplResidue *r = m->new_residue("WAT");
	TmplAtom *atom_H2 = m->new_atom("H2", Element(1));
	r->add_atom(atom_H2);
	c.set_xyz(0.9572000000,0.0000000000,0.0000000000);
	atom_H2->set_coord(c);
	TmplAtom *atom_O = m->new_atom("O", Element(8));
	r->add_atom(atom_O);
	c.set_xyz(-0.2399879329,0.9266270189,0.0000000000);
	atom_O->set_coord(c);
	TmplAtom *atom_H1 = m->new_atom("H1", Element(1));
	r->add_atom(atom_H1);
	c.set_xyz(0.0000000000,0.0000000000,0.0000000000);
	atom_H1->set_coord(c);
	(void) m->new_bond(atom_H2, atom_O);
	(void) m->new_bond(atom_O, atom_H1);
	return r;
}

void
restmpl_init_general(ResInitMap *rim)
{
	(*rim)[std::string("WAT")].middle = init_TIP3;
}
