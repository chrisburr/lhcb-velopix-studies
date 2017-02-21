# [SublimeLinter flake8-max-line-length:100]
from __future__ import division
from __future__ import print_function

from collections import defaultdict
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
R.gROOT.ProcessLine(".x lhcbstyle.C")

base_dir = '.'

files = [
    (join(base_dir, '154464562/Brunel-histos.root'), (R.kBlack, 20), "Nominal"),
    (join(base_dir, '154465308/Brunel-histos.root'), (R.kRed, 20), "Also nominal"),
]

prefix = 'plots/'

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


def make_resolution_plots():
    plots = defaultdict(list)
    # We have to keep references to any files we open to prevent ROOT from closing them
    open_files = []

    for (fname, colour, title) in files:
        if isinstance(colour, tuple):
            colour, marker = colour
        else:
            marker = 20

        f = R.TFile(fname)
        open_files.append(f)
        print("File:", fname)

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
            print("****", name)
            h = f.Get(opts['path'])

            if not h:
                print(">>>", name, "not found")
                continue

            h.GetXaxis().SetTitle(opts['xlabel'])
            h.GetYaxis().SetTitle(opts['ylabel'])
            h.SetLineColor(colour)
            h.SetMarkerColor(colour)
            h.SetMarkerStyle(marker)
            h.SetTitle(title)

            # turn mm into micron on y axis
            if "IP" in name or "Ntrk" in name:
                print("mm to micron for:", name)
                h.Scale(1000)

            if "IP3D" in name:
                h.GetYaxis().SetRangeUser(0, 160)

            if "IPx" in name or "IPy" in name:
                h.GetYaxis().SetRangeUser(0, 100)

            if name.startswith("IP"):
                print("Now fitting:", name)
                hist = R.TF1(
                    fname.replace(".", "_")+"_"+str(name),
                    "pol1",
                    h.GetXaxis().GetXmin(),
                    h.GetXaxis().GetXmax()
                )
                hist.SetLineColor(colour)
                h.Fit(hist)
                hist.SetLineColor(colour)
                print("Done.")
                print()

            if "Ntrk" in name:
                h.GetYaxis().SetRangeUser(0, 30)

            if "PVzNtrk" in name:
                h.GetYaxis().SetRangeUser(0, 170)

            if name in ("PVx", "PVy", "PVz"):
                h.Rebin(2)
                h.Scale(1./h.Integral())
                h.GetYaxis().SetRangeUser(0, 0.08*2)

            if "InvPt" in name:
                h.Scale(1./h.Integral())
                h.GetYaxis().SetRangeUser(0, 0.08*2)

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

    map(R.TFile.Close, open_files)


if __name__ == '__main__':
    make_resolution_plots()
