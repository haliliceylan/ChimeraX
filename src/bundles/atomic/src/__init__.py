# vim: set expandtab shiftwidth=4 softtabstop=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2016 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  For details see:
# http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html
# This notice must be embedded in or attached to all copies,
# including partial copies, of the software or any revisions
# or derivations thereof.
# === UCSF ChimeraX Copyright ===

from .molobject import Atom, Bond, Chain, CoordSet, Element, Pseudobond, Residue, Sequence, \
    StructureSeq, PseudobondManager, ChangeTracker
from .molobject import SeqMatchMap, estimate_assoc_params, try_assoc, StructAssocError
# pbgroup must precede molarray since molarray uses interatom_pseudobonds in global scope
from .pbgroup import PseudobondGroup, all_pseudobond_groups, interatom_pseudobonds, selected_pseudobonds
from .molarray import Collection, Atoms, AtomicStructures, Bonds, Chains, Pseudobonds, \
    PseudobondGroups, Residues, concatenate
from .structure import AtomicStructure, Structure, LevelOfDetail
from .structure import selected_atoms, selected_bonds
from .structure import all_atoms, all_atomic_structures, all_structures
from .structure import structure_atoms, structure_residues, structure_graphics_updater, level_of_detail
from .structure import PickedAtom, PickedBond, PickedResidue, PickedPseudobond
from .molsurf import buried_area, MolecularSurface, surfaces_with_atoms
from .changes import check_for_changes
from .pdbmatrices import biological_unit_matrices
from .triggers import get_triggers
from .mmcif import open_mmcif
from .pdb import open_pdb
from .search import atom_search_tree
from .shapedrawing import AtomicShapeDrawing


from chimerax.core.toolshed import BundleAPI

class _AtomicBundleAPI(BundleAPI):

    @staticmethod
    def get_class(class_name):
        if class_name in ["Atom", "AtomicStructure", "AtomicStructures", "Atoms", "Bond", "Bonds",
                "Chain", "Chains", "CoordSet", "LevelOfDetail", "MolecularSurface",
                "PseudobondGroup", "PseudobondManager", "Pseudobond", "Pseudobonds", "Residue",
                "Residues", "SeqMatchMap", "Sequence", "Structure", "StructureSeq"]:
            import importlib
            this_mod = importlib.import_module(".", __package__)
            return getattr(this_mod, class_name)
        elif class_name in ["AttrRegistration", "CustomizedInstanceManager", "_NoDefault",
                "RegAttrManager"]:
            from . import attr_registration
            return getattr(attr_registration, class_name)
        elif class_name == "XSectionManager":
            from . import ribbon
            return ribbon.XSectionManager

    @staticmethod
    def include_dir(bundle_info):
        from os.path import dirname, join
        return join(dirname(__file__), "include")

    @staticmethod
    def initialize(session, bundle_info):
        """Install alignments manager into existing session"""

        #TODO: set data path; generate presets menu
        from os.path import dirname, join
        Residue.set_templates_dir(join(dirname(__file__), "data"))

    @staticmethod
    def library_dir(bundle_info):
        from os.path import dirname, join
        return join(dirname(__file__), "lib")

bundle_api = _AtomicBundleAPI()
