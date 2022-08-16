# vim: set expandtab shiftwidth=4 softtabstop=4:

# === UCSF ChimeraX Copyright ===
# Copyright 2022 Regents of the University of California.
# All rights reserved. This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use. For details see:
# http://www.rbvi.ucsf.edu/chimerax/docs/licensing.html
# This notice must be embedded in or attached to all copies,
# including partial copies, of the software or any revisions
# or derivations thereof.
# === UCSF ChimeraX Copyright ===

class DICOMMetadata:
    def __init__(self, session, dicom_file):
        """Bring up a tool to view fine-grained metadata in DICOM files.
        session: A ChimeraX session
        dicom_file: The data structure returned by pydicom.dcmread()
        """
        self.session = session
        self.dicom_file = dicom_file

    def build_ui(self):
        pass
