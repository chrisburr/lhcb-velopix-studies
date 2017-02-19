# [SublimeLinter flake8-max-line-length:150]
# import ROOT
# import os
# import sys
# import subprocess
from ROOT import (
    TFile, TCanvas, TH1F, TH2F, gROOT, TF1, gStyle, TText, TMath, Double
)
import Panoramix
from LHCbConfig import ApplicationMgr, INFO, EventSelector, lhcbApp, CondDB, addDBTags
from LHCbMath import XYZVector
# from Configurables import CondDB, LHCbApp
# from LHCbConfig import *
from TrackFitter.ConfiguredFitters import ConfiguredMasterFitter

import GaudiPython
from GaudiConf import IOHelper
# from gaudigadgets import panorewind
from LinkerInstances.eventassoc import linkedTo
# from LinkerInstances.eventassoc import *

LineTraj = GaudiPython.gbl.LHCb.LineTraj
MCParticle = GaudiPython.gbl.LHCb.MCParticle
Track = GaudiPython.gbl.LHCb.Track


def plot_ip(hist, hist_max, filename):
    c1 = TCanvas('c1', '', 750, 500)
    c1.cd()
    hist.SetStats(0)
    hist.SetMinimum(0.)
    hist.SetMaximum(hist_max)
    fun = TF1('pol1', 'pol1')
    hist.Fit(fun)
    a0 = fun.GetParameter(0)*1000.
    a1 = fun.GetParameter(1)*1000.
    # txt = 'Sigma=%4.1f+%4.1f/pt'
    txt = 'Sigma='+'%4.1f' % (a0)+'+'+'%4.1f' % (a1)+'/pt'
    tx = TText(0.25, 0.1, txt)
    tx.DrawText(0.25, 0.1, txt)
    c1.Print(filename+'resolution.png')


def myFitSliceY(h):
    N = h.GetNbinsX()
    name = h.GetName()
    t = TCanvas('t_'+name, h.GetTitle(), 1600, 1200)
    #
    g = TF1('g', 'gaus')
    myprof = TH1F()
    h.ProjectionX(name+'_myprof').Copy(myprof)
    myprof.SetName(name+'_myprof')
    myprof.SetTitle('sigma, '+h.GetTitle())
    #
    nw = int(TMath.Sqrt(N)+0.5)
    nh = int(N/nw)
    while nh*nw < N:
        nh += 1
    t.Divide(nw, nh)
    for n in range(1, N+1):
        test = h.ProjectionY(name+'_ProjY_'+str(n), n, n)
        test.SetTitle(h.GetTitle())
        if test.GetEntries() > 50:
            t.cd(n)
            test.Fit(g)
            test.DrawCopy()
            ypos = test.GetMaximum()*0.1
            sigma = g.GetParameter(2)
            error = g.GetParError(2)
            txt = 'Sigma='+'%4.2f' % (sigma)
            tx = TText(-0.04, ypos, txt)
            tx.DrawText(-0.04, ypos, txt)
            myprof.SetBinContent(n, sigma)
            myprof.SetBinError(n, error)
    return t, myprof


def print_sigma(h):
    fun = TF1('g', 'gaus')
    h.Fit(fun)
    h.DrawCopy()
    a0 = fun.GetParameter(1)
    a1 = fun.GetParameter(2)
    ea0 = fun.GetParError(1)
    ea1 = fun.GetParError(2)
    if a0 < 0.01:
        a0 = a0*1000.
        ea0 = ea0*1000.
        txt = 'Mean='+'(%4.2f' % (a0)+'+/-'+'%4.2f' % (ea0)+')*10E-3'
    else:
        txt = 'Mean='+'%4.2f' % (a0)+'+/-'+'%4.2f' % (ea0)
    height = h.GetMaximum()*0.94
    posx = h.GetBinLowEdge(2)
    tx = TText(posx, height, txt)
    tx.DrawText(posx, height, txt)
    if a1 < 0.01:
        a1 = a1*1000.
        ea1 = ea1*1000.
        txt = 'Sigma='+'(%4.2f' % (a1)+'+/-'+'%4.2f' % (ea1)+')*10E-3'
    else:
        txt = 'Sigma='+'%4.2f' % (a1)+'+/-'+'%4.2f' % (ea1)
    height = h.GetMaximum()*0.86
    tx = TText(posx, height, txt)
    tx.DrawText(posx, height, txt)


def run_script():
    Range = GaudiPython.gbl.std.pair('double', 'double')

    Nevents = 5000
    optSlope = 6

    slopemin = [0,     0.025, 0.05,  0.075, 0.1,   0.125,  0]
    slopemax = [0.025, 0.05,  0.075, 0.1,   0.125, 0.15,  10.]

    files = ['/afs/cern.ch/work/c/cburr/Brunel.xdst']

    lhcbApp.DataType = 'Upgrade'
    lhcbApp.setProp(
        "Detectors",
        ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Spd', 'Prs', 'Ecal', 'Hcal', 'Muon', 'Magnet']
    )
    CondDB().Upgrade = True

    IOHelper('ROOT').inputFiles(files)
    addDBTags(files[0])

    ConfiguredMasterFitter("TrackMasterFitter")
    ApplicationMgr(OutputLevel=INFO, AppName='IPandPresol')

    EventSelector().PrintFreq = 100
    appMgr = GaudiPython.AppMgr()

    evt = appMgr.evtsvc()

    h_IP = TH2F('h_IP', ' IP for long tracks vs. 1/pt', 25, 0., 5.,  100, -0.5, 0.5)
    h_IPx = TH2F('h_IPx', ' IPx for long tracks vs. 1/pt', 25, 0., 5., 100, -0.5, 0.5)
    h_IPy = TH2F('h_IPy', ' IPy for long tracks vs. 1/pt', 25, 0., 5., 100, -0.5, 0.5)
    h_IPz = TH2F('h_IPz', ' IPz for long tracks vs. 1/pt', 25, 0., 5., 100, -0.5, 0.5)
    h_P = TH2F('h_P', ' delp/p for long tracks vs. p', 25, 0., 150., 100, -0.04, 0.04)
    h_sx = TH2F('h_sx', ' res slope x for long tracks vs. p', 25, 0., 150., 100, -0.005, 0.005)
    h_sy = TH2F('h_sy', ' res slope y for long tracks vs. p', 25, 0., 150., 100, -0.005, 0.005)
    p_P = TH2F('p_P', ' pull delp/p for long tracks vs. p', 25, 0., 150., 100, -5.0, 5.0)
    p_IPx = TH2F('p_IPx', ' pull delx for long tracks vs. p', 25, 0., 5., 100, -5.0, 5.0)
    p_IPy = TH2F('p_IPy', ' pull dely for long tracks vs. p', 25, 0., 5., 100, -5.0, 5.0)
    p_sx = TH2F('p_sx', 'pull res slope x for long tracks vs. p', 25, 0., 150., 100, -5.0, 5.0)
    p_sy = TH2F('p_sy', 'pull res slope y for long tracks vs. p', 25, 0., 150., 100, -5.0, 5.0)
    h_pmc = TH2F('h_pmc', 'p mc vs p rec ', 25, 0., 150.,  25, 0., 150.)
    h_firstHit = TH1F('h_firstHit', ' r of first measured point', 100, 0.0, 50.0)

    poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
    extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
    Panoramix.getTool('TrackMasterFitter', 'ITrackFitter')
    appMgr.toolsvc().create('TrackInitFit', 'ITrackFitter')

    for k in range(Nevents):
        appMgr.run(1)
        cont = evt['Rec/Track/Best']
        if not cont:
            break

        l2mc = linkedTo(MCParticle, Track, 'Rec/Track/Best')
        for t in cont:
            if t.type() != t.Long:
                continue
            # only take tracks within a given slope range
            fst = t.firstState()
            tx = fst.tx()
            ty = fst.ty()
            slope = TMath.Sqrt(tx*tx+ty*ty)
            if slope < slopemin[optSlope] or slope > slopemax[optSlope]:
                continue
            # only take tracks with unique link to MC truth
            if l2mc.range(t).size() != 1:
                continue
            # MC part
            mcp = l2mc.first(t)
            # remove electrons
            if mcp.particleID().abspid() == 11:
                continue
            ovx = mcp.originVertex().position()
            # only take tracks close to beamline
            if ovx.rho() > 1.:
                continue
            mom = mcp.momentum()
            one_over_pt = 1./mom.pt()*1000.
            p = mom.P()
            for s in t.states():
                if s.location() == s.FirstMeasurement:
                    pos = s.position()
                    h_firstHit.Fill(pos.rho())
                    break
            # extrapolate to mc origin vertex
            astate = t.firstState().clone()
            result = extrap.propagate(astate, ovx.z())
            traj = LineTraj(astate.position(), astate.slopes(), Range(-1000., 1000.))
            dis = XYZVector()
            s = Double(0.1)
            a = Double(0.0005)
            success = poca.minimize(traj, s, ovx, dis, a)
            print(s, a)
            if success.isFailure() > 0:
                continue
            ip = dis.r()
            if dis.z() < 0:
                ip = -ip
            p_ontrack = traj.position(s)
            ipx = p_ontrack.x()-ovx.x()
            ipy = p_ontrack.y()-ovx.y()
            ipz = p_ontrack.z()-ovx.z()

            # Fill histograms
            h_IP.Fill(one_over_pt, ip)
            h_IPx.Fill(one_over_pt, ipx)
            h_IPy.Fill(one_over_pt, ipy)
            h_IPz.Fill(one_over_pt, ipz)
            delp = (t.p()-p)/p
            h_P.Fill(p/1000., delp)
            h_pmc.Fill(t.p()/1000., p/1000.)
            delsx = (astate.tx()-mom.x()/mom.z())
            delsy = (astate.ty()-mom.y()/mom.z())
            h_sx.Fill(p/1000., delsx)
            h_sy.Fill(p/1000., delsy)
            # pull plots
            p_P.Fill(p/1000., (delp*p)/(TMath.Sqrt(astate.errQOverP2())*t.p()*t.p()))
            p_IPx.Fill(one_over_pt, ipx/TMath.Sqrt(astate.errX2()))
            p_IPy.Fill(one_over_pt, ipy/TMath.Sqrt(astate.errY2()))
            p_sx.Fill(p/1000., delsx/TMath.Sqrt(astate.errTx2()))
            p_sy.Fill(p/1000., delsy/TMath.Sqrt(astate.errTy2()))

    f = TFile('IPandPresol_'+str(optSlope)+'_upgrade.root', 'recreate')
    for h in gROOT.GetList():
        h.Write()
    f.Close()

    c1 = TCanvas('c1', '', 750, 500)

    tcp = TCanvas('tcp', 'momentum resolution', 750, 500)
    tcp.Divide(1, 1)
    tcp.cd(1)
    gStyle.SetOptFit(111)
    g = TF1('g', 'gaus')
    h_P.FitSlicesY(g)
    h_P_prof = gROOT.FindObjectAny('h_P_2')
    h_P_prof.SetMaximum(0.015)
    h_P_prof.SetMinimum(0.0)
    h_P_prof.SetTitle('Momentum resolution as function of p')
    h_P_prof.Draw()
    h_P_prof.Fit('pol1')
    tcp.Print('MomentumResolution.png')

    tr = TCanvas('tr', 'minimum r', 750, 500)
    tr.Divide(1, 1)
    tr.cd(1)
    h_firstHit.Draw()
    gStyle.SetOptFit(111)
    tr.Print('radiusOfFirstMeasurement.png')

    tipx, h_IPx_myprof = myFitSliceY(h_IPx)
    c1.cd()
    h_IPx_myprof.Draw()
    h_IPx_myprof.Fit('pol1')

    tipy, h_IPy_myprof = myFitSliceY(h_IPy)
    c1.cd()
    h_IPy_myprof.Draw()
    h_IPy_myprof.Fit('pol1')

    tipz, h_IPz_myprof = myFitSliceY(h_IPz)
    c1.cd()
    h_IPz_myprof.Draw()
    h_IPz_myprof.Fit('pol1')

    h_IPxy_myprof = TH1F()
    h_IPx_myprof.Copy(h_IPxy_myprof)
    h_IPxy_myprof.SetName('h_IPxy_myprof')
    h_IPxy_myprof.SetTitle('sigma IP as function of 1/pt')
    for n in range(1, h_IPx_myprof.GetNbinsX()+1):
        sx = h_IPx_myprof.GetBinContent(n)
        sy = h_IPy_myprof.GetBinContent(n)
        sz = h_IPz_myprof.GetBinContent(n)
        sigma = TMath.Sqrt(sx*sx + sy*sy + sz*sz)
        h_IPxy_myprof.SetBinContent(n, sigma)
        ex = h_IPx_myprof.GetBinError(n)
        ey = h_IPy_myprof.GetBinError(n)
        ez = h_IPz_myprof.GetBinError(n)
        error = TMath.Sqrt(sx*sx*ex*ex + sy*sy*ey*ey + sz*sz*ez*ez)/sigma
        h_IPxy_myprof.SetBinError(n, error)

    plot_ip(h_IPxy_myprof, 0.1, 'IP')
    plot_ip(h_IPx_myprof, 0.1, 'IPX')
    plot_ip(h_IPy_myprof, 0.1, 'IPY')
    plot_ip(h_IPz_myprof, 0.1, 'IPZ')

    tp, h_p_myprof = myFitSliceY(h_P)

    gStyle.SetOptFit(0)

    tpull = TCanvas('tpull', 'pull distributions', 1200, 800)
    tpull.Divide(3, 2)
    tpull.cd(1)
    h = p_IPx.ProjectionY()
    h.SetTitle('Pull distribution IPx')
    print_sigma(h)
    tpull.cd(2)
    h = p_IPy.ProjectionY()
    h.SetTitle('Pull distribution IPy')
    print_sigma(h)
    tpull.cd(4)
    h = p_sx.ProjectionY()
    h.SetTitle('Pull distribution slope x')
    print_sigma(h)
    tpull.cd(5)
    h = p_sy.ProjectionY()
    h.SetTitle('Pull distribution slope y')
    print_sigma(h)
    tpull.cd(6)
    h = p_P.ProjectionY()
    h.SetTitle('Pull distribution p')
    print_sigma(h)
    tpull.Print('pulls.png')

    tres = TCanvas('tres', 'resolutions', 1200, 800)
    tres.Divide(3, 2)
    tres.cd(1)
    h = h_IPx.ProjectionY()
    h.SetTitle('resolution IPx')
    print_sigma(h)
    tres.cd(2)
    h = h_IPy.ProjectionY()
    h.SetTitle('resolution IPy')
    print_sigma(h)
    tres.cd(4)
    h = h_sx.ProjectionY()
    h.SetTitle('resolution slope x')
    print_sigma(h)
    tres.cd(5)
    h = h_sy.ProjectionY()
    h.SetTitle('resolution slope y')
    print_sigma(h)
    tres.cd(6)
    h = h_P.ProjectionY()
    h.SetTitle('resolution p')
    print_sigma(h)
    tres.Print('resolution.png')


run_script()
