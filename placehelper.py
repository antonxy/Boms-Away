#!/usr/bin/env python2
import os
from boms_away import sch
from boms_away import kicad_helpers as kch
import argparse
import subprocess

import wx

class ScanFrame(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, path):
        wx.Frame.__init__(self, parent, title="Scan here", size=(200,100))
        self.components = []
        self.read_sch(path)

        self.current_components = []
        self.last_selected = None

        self.control = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter, self.control)
        self.Show(True)

    def read_sch(self, path):
        base_dir = os.path.split(path)[0]
        top_sch = os.path.split(path)[-1]
        top_name = os.path.splitext(top_sch)[0]

        schematics = {}
        schematics[top_name] = (
            sch.Schematic(os.path.join(base_dir, top_sch))
        )

        # Recursively walks sheets to locate nested subschematics
        # TODO: re-work this to return values instead of passing them byref
        kch.walk_sheets(base_dir, schematics[top_name].sheets, schematics)

        for name, schematic in list(schematics.items()):
            for _cbase in schematic.components:
                c = kch.ComponentWrapper(_cbase)

                # Skip virtual components (power, gnd, etc)
                if c.is_virtual:
                    continue

                # Skip anything that is missing either a value or a
                # footprint
                if not c.has_valid_key_fields:
                    continue

                c.add_bom_fields()
                self.components.append(c)

    def OnEnter(self, event):
        scanned = self.control.GetValue()
        self.control.SetValue("")
        if scanned != "":
            comps = self.find_component(scanned)
            self.current_components = comps
        if len(self.current_components) > 0:
            comp = self.current_components.pop()
            print(comp)
            self.select_by_ref(comp.reference)

    def select_by_ref(self, ref):
        subprocess.call(["xdotool", "search", "--name", "pcbnew", "key", "ctrl+f"])
        subprocess.call(["xdotool", "search", "--name", "pcbnew", "type", ref])
        subprocess.call(["xdotool", "search", "--name", "pcbnew", "key", "Return", "Escape"])
        #if self.last_selected is not None:
        #    mod = self.last_selected
        #    for p in mod.Pads():
        #        p.ClearSelected()
        #    for p in mod.GraphicalItems():
        #        p.ClearSelected()
        #    mod.ClearSelected()
        #mod = pcbnew.GetBoard().FindModuleByReference(ref)
        #if mod is not None:
        #    for p in mod.Pads():
        #        p.SetSelected()
        #    for p in mod.GraphicalItems():
        #        p.SetSelected()
        #    mod.SetSelected()
        #self.last_selected = mod
        #pcbnew.Refresh()

    def find_component(self, scanned):
        scanned = scanned.strip()
        matching_comps = []
        for c in self.components:
            if c.manufacturer_pn.strip() == scanned or c.supplier_pn.strip() == scanned:
                matching_comps.append(c)
        return matching_comps

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pcbnew manual PnP helper')
    parser.add_argument('path', type=str, help='Path of the eeschema .sch file beloning to the PCB')
    args = parser.parse_args()

    app = wx.App(False)
    frame = ScanFrame(None, args.path)
    app.MainLoop()
