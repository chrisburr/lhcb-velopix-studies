# [SublimeLinter flake8-max-line-length:100]
from __future__ import division
from __future__ import print_function

from collections import defaultdict
from glob import glob
from os.path import join

import ROOT as R

try:
    R.TArray
except SystemError:
    pass

# Don't try to display any TCanvases
R.gROOT.SetBatch(True)
# Don't draw titles
R.gStyle.SetOptTitle(0)
R.gROOT.ProcessLine(".x assets/lhcbStyle.C")

base_dir = 'output/scenarios'

files = [
    (join(base_dir, 'tip_x=0_y=-10000um/hists.root'), (R.kOrange, 20), "tip_x=0_y=-10000um"),
    (join(base_dir, 'tip_x=0_y=-1000um/hists.root'), (R.kCyan, 20), "tip_x=0_y=-1000um"),
    (join(base_dir, 'tip_x=0_y=-100um/hists.root'), (R.kRed, 20), "tip_x=0_y=-100um"),
    (join(base_dir, 'Original/hists.root'), (R.kBlack, 20), "Original"),
    (join(base_dir, 'tip_x=0_y=+100um/hists.root'), (R.kBlue, 20), "tip_x=0_y=+100um"),
    (join(base_dir, 'tip_x=0_y=+1000um/hists.root'), (R.kYellow+3, 20), "tip_x=0_y=+1000um"),
    (join(base_dir, 'tip_x=0_y=+10000um/hists.root'), (R.kGreen+3, 20), "tip_x=0_y=+10000um"),
]

prefix = 'output/plots/'

figs = {
    "IPx": {
        'path': "IPxVsInvTruePtH2_2",
        'xlabel': "1/#it{p}_{T} [GeV^{-1}#it{c}]",
        'ylabel': "IP_{x} resolution [#mum]",
    },
    "IPy": {
        'path': "IPyVsInvTruePtH2_2",
        'xlabel': "1/#it{p}_{T} [GeV^{-1}#it{c}]",
        'ylabel': "IP_{y} resolution [#mum]",
    },
    "IP3Dprofile": {
        'path': "IP3DVsInvTruePtH2_pfx",
        'xlabel': "1/#it{p}_{T} [GeV^{-1}#it{c}]",
        'ylabel': "IP_{3D} resolution [#mum]",
     },
    "PVx": {
        'path': "TrackIPResolutionChecker/PV/dxH1",
        'xlabel': "#it{x}_{PV} - #it{x}_{PV,true} [mm]",
        'ylabel': "Normalised",
    },
    "PVy": {
        'path': "TrackIPResolutionChecker/PV/dyH1",
        'xlabel': "#it{y}_{PV} - #it{y}_{PV,true} [mm]",
        'ylabel': "Normalised",
    },
    "PVz": {
        'path': "TrackIPResolutionChecker/PV/dzH1",
        'xlabel': "#it{z}_{PV} - #it{z}_{PV,true} [mm]",
        'ylabel': "Normalised",
    },
    "PVxNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVXResolutionVsNTrk",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
    },
    "PVyNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVYResolutionVsNTrk",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
    },
    "PVzNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVZResolutionVsNTrk",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
    },
}

# ****** plan-B studies
# =================================

# == TDR vs A vs B


def get_plot(fname, colour, marker, title):
    f = R.TFile(fname)

    # For each file take the 2D histogram and fit it to create
    # the histogram containing the mean of the 3D difference
    # as function of inverse pT
    ip3d_vs_invpt = f.Get("TrackIPResolutionChecker/IP/Velo/IP3DVsInvTruePtH2")
    ip3d_vs_invpt.ProfileX()
    ip3d_vs_invpt.FitSlicesY()

    ipx_vs_invpt = f.Get("TrackIPResolutionChecker/IP/Velo/IPxVsInvTruePtH2")
    ipx_vs_invpt.FitSlicesY()

    ipy_vs_invpt = f.Get("TrackIPResolutionChecker/IP/Velo/IPyVsInvTruePtH2")
    ipy_vs_invpt.FitSlicesY()

    PVx_vs_Ntrk = f.Get("TrackIPResolutionChecker/PV/dxVersusNTrk")
    PVy_vs_Ntrk = f.Get("TrackIPResolutionChecker/PV/dyVersusNTrk")
    PVz_vs_Ntrk = f.Get("TrackIPResolutionChecker/PV/dzVersusNTrk")
    PVx_vs_Ntrk.FitSlicesY()
    PVz_vs_Ntrk.FitSlicesY()
    PVy_vs_Ntrk.FitSlicesY()

    for name, opts in figs.items():
        h = f.Get(opts['path'])
        print(name, fname, opts['path'], h)
        assert h

        h.GetXaxis().SetTitle(opts['xlabel'])
        h.GetYaxis().SetTitle(opts['ylabel'])
        h.SetLineColor(colour)
        h.SetMarkerColor(colour)
        h.SetMarkerStyle(marker)
        h.SetTitle(title)

        # turn mm into micron on y axis
        if "IP" in name or "Ntrk" in name:
            h.Scale(1000)

        if name.startswith("IP"):
            hist = R.TF1(
                fname.replace(".", "_")+"_"+str(name),
                "pol1",
                h.GetXaxis().GetXmin(),
                h.GetXaxis().GetXmax()
            )
            hist.SetLineColor(colour)
            h.Fit(hist)
            hist.SetLineColor(colour)

        if name in ("PVx", "PVy", "PVz"):
            h.Rebin(2)
            h.Scale(1./h.Integral())

        if "InvPt" in name:
            h.Scale(1./h.Integral())

        h.SetDirectory(0)
        yield name, h


def make_resolution_plots():
    plots = defaultdict(list)
    for (fname, (colour, marker), title) in files:
        # Average the matching histograms together
        _plots = {}
        for _fname in glob(fname):
            for name, h in get_plot(_fname, colour, marker, title):
                h.SetBit(R.TH1.kIsAverage)
                if name in _plots:
                    _plots[name].Add(h)
                else:
                    _plots[name] = h
        # Add the averaged histograms to the main dictionary
        for name, h in _plots.items():
            set_hist_range(name, h)
            plots[name].append(h)

    c = R.TCanvas("wer", "wie was", 750, 500)
    for name, figs_ in plots.items():
        figs_[0].SetStats(0)
        figs_[0].Draw()

        leg_x, leg_y = 0.6, 0.2
        leg_w, leg_h = 0.25, 0.15
        if "Ntrk" in name or "PV" in name:
            leg_x, leg_y = 0.6, 0.6

        leg = R.TLegend(leg_x, leg_y, leg_x+leg_w, leg_y+leg_h)
        leg.SetFillColorAlpha(0, 0)
        leg.SetLineColorAlpha(0, 0)

        leg.AddEntry(figs_[0], figs_[0].GetTitle())

        for f in figs_[1:]:
            f.Draw("same")
            leg.AddEntry(f, f.GetTitle())

        R.TLatex().DrawLatexNDC(0.20, 0.80, "LHCb simulation")
        c.RedrawAxis()
        leg.Draw()

        # c.SaveAs(prefix + name + ".pdf")
        c.SaveAs(prefix + name + ".png")


def set_hist_range(name, hist):
    if "IP3D" in name:
        hist.GetYaxis().SetRangeUser(0, 160)

    if "IPx" in name or "IPy" in name:
        hist.GetYaxis().SetRangeUser(0, 100)

    if "Ntrk" in name:
        hist.GetYaxis().SetRangeUser(0, 30)

    if "PVzNtrk" in name:
        hist.GetYaxis().SetRangeUser(0, 170)

    if name in ("PVx", "PVy", "PVz"):
        hist.GetYaxis().SetRangeUser(0, 0.08*2)

    if "InvPt" in name:
        hist.GetYaxis().SetRangeUser(0, 0.08*2)


if __name__ == '__main__':
    make_resolution_plots()
