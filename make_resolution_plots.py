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


R.gROOT.SetBatch(True)
# R.gROOT.ProcessLine(".x lhcbstyle.C")
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
        'ylabeloffset': 1.002,
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
        'ylabeloffset': 1.05,
     },
    "PVx": {
        'path': "TrackIPResolutionChecker/PV/dxH1",
        'xlabel': "#it{x}_{PV} - #it{x}_{PV,true} [mm]",
        'ylabel': "Normalised",
        'ylabeloffset': 1.18,
    },
    "PVy": {
        'path': "TrackIPResolutionChecker/PV/dyH1",
        'xlabel': "#it{y}_{PV} - #it{y}_{PV,true} [mm]",
        'ylabel': "Normalised",
        'ylabeloffset': 1.13,
    },
    "PVz": {
        'path': "TrackIPResolutionChecker/PV/dzH1",
        'xlabel': "#it{z}_{PV} - #it{z}_{PV,true} [mm]",
        'ylabel': "Normalised",
        'ylabeloffset': 1.18,
    },
    "PVxNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVXResolutionVsNTrk",
        # 'path': "dxVersusNTrk_2",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
    },
    "PVyNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVYResolutionVsNTrk",
        # 'path': "dyVersusNTrk_2",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
    },
    "PVzNtrk": {
        'path': "TrackIPResolutionChecker/PV/PVZResolutionVsNTrk",
        # 'path': "dzVersusNTrk_2",
        'xlabel': "Number of tracks",
        'ylabel': "Average resolution [#mum]",
        'ylabeloffset': 1.1,
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

            maxy = 100
            if prefix.startswith("Massi"):
                maxy = 60

            if "IP3D" in name:
                if "zoom" in prefix:
                    h.GetYaxis().SetRangeUser(15, 75)
                else:
                    h.GetYaxis().SetRangeUser(0, maxy)  # 160)

            if ("IPx" in name) or ("IPy" in name):
                if "zoom" in prefix:
                    h.GetYaxis().SetRangeUser(10, 55)
                else:
                    h.GetYaxis().SetRangeUser(0, maxy)

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

    c = R.TCanvas("wer", "wie was", 615, 615)
    c.SetLeftMargin(0.16)
    c.SetTopMargin(0.03)
    for name, figs_ in plots.items():
        c.Clear()
        if not figs_:
            print("Skipping:", name)
            continue

        figs_[0].Draw()
        if "Ntrk" in name:
            leg = R.TLegend(0.6, 0.6, 0.9, 0.85)
        else:
            leg = R.TLegend(0.18, 0.7, 0.6, 0.88)

        leg.SetFillColor(0)

        leg.AddEntry(figs_[0], figs_[0].GetTitle())

        # Draw 1/pT distribution of tracks
        if "IP" in name:
            key = "InvPt"
            if key in plots:
                h = plots[key][0].Clone()
                h.SetLineColor(R.kGray+1)
                h.Scale(220/3)
                h.Draw("same hist")

        if name in figs and "ylabeloffset" in figs[name]:
            figs_[0].GetYaxis().SetTitleOffset(figs[name]['ylabeloffset'])

        for f in figs_[1:]:
            f.Draw("same")
            leg.AddEntry(f, f.GetTitle())

        stamp = R.TLatex(0.20, 0.90, "LHCb simulation")
        stamp.SetNDC(True)
        stamp.Draw()
        c.RedrawAxis()
        leg.Draw()

        # c.SaveAs(prefix + name + ".pdf")
        c.SaveAs(prefix + name + ".png")

    for (fname, colour, title) in files:
        f = R.TFile(fname)
        f.Close()


if __name__ == '__main__':
    make_resolution_plots()
