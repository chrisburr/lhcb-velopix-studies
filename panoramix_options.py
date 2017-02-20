# [SublimeLinter flake8-max-line-length:150]
from __future__ import division
from __future__ import print_function

from math import sqrt

import pandas as pd

from ROOT import (
    TFile, TCanvas, TH1F, TH2F, gROOT, TF1, gStyle, TText, Double
)
import Panoramix
from LHCbConfig import ApplicationMgr, INFO, EventSelector, lhcbApp, CondDB, addDBTags
from LHCbMath import XYZVector
from TrackFitter.ConfiguredFitters import ConfiguredMasterFitter
import GaudiPython
from GaudiConf import IOHelper
from LinkerInstances.eventassoc import linkedTo

LineTraj = GaudiPython.gbl.LHCb.LineTraj
MCParticle = GaudiPython.gbl.LHCb.MCParticle
Track = GaudiPython.gbl.LHCb.Track
Range = GaudiPython.gbl.std.pair('double', 'double')

files = [
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917952/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917957/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917961/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917972/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917978/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917983/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917987/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917991/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917993/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917996/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917943/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917950/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917953/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917958/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917962/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917974/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917979/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917982/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917986/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917989/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917954/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917959/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917963/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917975/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917977/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917981/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917985/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917990/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917994/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917997/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917936/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917937/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917938/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917939/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917940/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917941/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917942/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917948/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917951/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917955/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917956/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917960/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917973/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917976/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917980/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917984/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917988/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917992/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917995/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917998/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918016/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918031/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918040/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918054/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918067/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918077/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918091/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918100/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918112/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153918/153918129/Brunel.xdst',
    'root://eoslhcb.cern.ch//eos/lhcb/grid/user/lhcb/user/c/cburr/2017_02/153917/153917999/Brunel.xdst'
]


def run_script():
    optSlope = 6

    slopemin = [0,     0.025, 0.05,  0.075, 0.1,   0.125,  0]
    slopemax = [0.025, 0.05,  0.075, 0.1,   0.125, 0.15,  10.]

    lhcbApp.DataType = 'Upgrade'
    lhcbApp.setProp(
        "Detectors",
        ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Spd', 'Prs', 'Ecal', 'Hcal', 'Muon', 'Magnet']
    )
    CondDB().Upgrade = True

    IOHelper('ROOT').inputFiles(files)
    addDBTags(files[0])
    # lhcbApp.DDDBtag = 'dddb-20160304'
    # lhcbApp.CondDBtag = 'sim-20150716-vc-md100'

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

    df = pd.DataFrame(columns=[
        'true_pid', 'track_type', 'true_rho',
        'true_p', 'true_pt', 'true_px', 'true_py', 'true_pz',
        'reco_p', 'reco_pt',
        'true_vertex_x', 'true_vertex_y', 'true_vertex_z',
        'reco_vertex_x', 'reco_vertex_xerr', 'reco_vertex_y', 'reco_vertex_yerr', 'reco_vertex_z',
        'reco_slope_x', 'reco_slope_xerr', 'reco_slope_y', 'reco_slope_yerr', 'reco_slope_errQOverP2'
    ])

    poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
    extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
    Panoramix.getTool('TrackMasterFitter', 'ITrackFitter')
    appMgr.toolsvc().create('TrackInitFit', 'ITrackFitter')

    while True:
        appMgr.run(1)
        if not evt['/Event/Rec/Header']:
            break

        track_to_mc = linkedTo(MCParticle, Track, 'Rec/Track/Best')
        for track in evt['Rec/Track/Best']:
            # Only use long tracks
            if track.type() != track.Long:
                continue
            # Only take tracks within a given slope range
            # TODO: Why???
            slope = sqrt(track.firstState().tx()**2 + track.firstState().ty()**2)
            if slope < slopemin[optSlope] or slope > slopemax[optSlope]:
                continue
            # Only take tracks with unique link to MC truth
            # TODO: Is this a good idea?
            if track_to_mc.range(track).size() != 1:
                continue
            # Find the MCParticle for this track
            mc_particle = track_to_mc.first(track)
            # Remove electrons
            if mc_particle.particleID().abspid() == 11:
                continue
            mc_vertex = mc_particle.originVertex().position()
            # Only take tracks close to beam line
            if mc_vertex.rho() > 1.:
                continue
            # Find the first hit from the reconstructed track
            for s in track.states():
                if s.location() == s.FirstMeasurement:
                    pos = s.position()
                    h_firstHit.Fill(pos.rho())
                    break
            # Get the MC momentum information
            true_momentum = mc_particle.momentum()
            one_over_pt = 1000. / true_momentum.pt()
            true_p = true_momentum.P()

            # Extrapolate to mc origin vertex
            astate = track.firstState().clone()
            extrap.propagate(astate, mc_vertex.z())
            traj = LineTraj(astate.position(), astate.slopes(), Range(-1000., 1000.))
            dis = XYZVector()
            s = Double(0.1)
            a = Double(0.0005)
            success = poca.minimize(traj, s, mc_vertex, dis, a)
            if success.isFailure() > 0:
                print('#'*60, 'TRACK FAILED')
                continue
            ip = dis.r()
            if dis.z() < 0:
                ip = -ip
            p_ontrack = traj.position(s)
            ipx = p_ontrack.x()-mc_vertex.x()
            ipy = p_ontrack.y()-mc_vertex.y()
            ipz = p_ontrack.z()-mc_vertex.z()

            df.loc[len(df)] = (
                mc_particle.particleID().pid(), int(track.type()), pos.rho(),
                true_momentum.P(), true_momentum.pt(),
                true_momentum.px(), true_momentum.py(), true_momentum.pz(),
                track.p(), track.pt(),
                mc_vertex.x(), mc_vertex.y(), mc_vertex.z(),
                p_ontrack.x(), sqrt(astate.errX2()),
                p_ontrack.y(), sqrt(astate.errY2()),
                p_ontrack.z(),
                astate.tx(), sqrt(astate.errTx2()), astate.ty(), sqrt(astate.errTy2()),
                sqrt(astate.errQOverP2())
            )

            # Fill histograms
            h_IP.Fill(one_over_pt, ip)
            h_IPx.Fill(one_over_pt, ipx)
            h_IPy.Fill(one_over_pt, ipy)
            h_IPz.Fill(one_over_pt, ipz)
            delta_p = (track.p()-true_p)/true_p
            h_P.Fill(true_p/1000., delta_p)
            h_pmc.Fill(track.p()/1000., true_p/1000.)
            delsx = (astate.tx()-true_momentum.x()/true_momentum.z())
            delsy = (astate.ty()-true_momentum.y()/true_momentum.z())
            h_sx.Fill(true_p/1000., delsx)
            h_sy.Fill(true_p/1000., delsy)
            # pull plots
            p_P.Fill(true_p/1000., (delta_p*true_p)/(sqrt(astate.errQOverP2()) * track.p()**2))
            p_IPx.Fill(one_over_pt, ipx/sqrt(astate.errX2()))
            p_IPy.Fill(one_over_pt, ipy/sqrt(astate.errY2()))
            p_sx.Fill(true_p/1000., delsx/sqrt(astate.errTx2()))
            p_sy.Fill(true_p/1000., delsy/sqrt(astate.errTy2()))

    df.to_json('VeloPix_studies.json')

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
    h_P_prof.SetStats(0)
    h_P_prof.Draw()
    h_P_prof.Fit('pol1')
    tcp.Print('MomentumResolution.png')

    tr = TCanvas('tr', 'minimum r', 750, 500)
    h_firstHit.SetStats(0)
    h_firstHit.Draw()
    gStyle.SetOptFit(111)
    tr.Print('radiusOfFirstMeasurement.png')

    plot_ip(h_IP, 0.1, 'IP')
    plot_ip(h_IPx, 0.1, 'IPX')
    plot_ip(h_IPy, 0.1, 'IPY')
    plot_ip(h_IPz, 0.1, 'IPZ')

    gStyle.SetOptFit(0)

    plot_split_canv('Pull distribution', [
        (p_IPx, 'IPx'), (p_IPy, 'IPy'), (None, None),
        (p_sx, 'slope x'), (p_sy, 'slope y'), (p_P, 'p')
    ])
    plot_split_canv('resolution', [
        (h_IPx, 'IPx'), (h_IPy, 'IPy'), (h_IPz, 'IPz'),
        (h_sx, 'slope x'), (h_sy, 'slope y'), (h_P, 'p')
    ])

    f = TFile('VeloPix_studies.root', 'recreate')
    for obj in gROOT.GetList():
        obj.Write()
    for obj in gROOT.GetListOfCanvases():
        obj.Write()
    gROOT.FindObjectAny('h_P_0').Write()
    gROOT.FindObjectAny('h_P_1').Write()
    gROOT.FindObjectAny('h_P_2').Write()
    gROOT.FindObjectAny('h_P_chi2').Write()
    f.Close()


def make_profile(h):
    N = h.GetNbinsX()
    name = h.GetName()
    t = TCanvas('t_'+name, h.GetTitle(), 1600, 1200)
    g = TF1('g', 'gaus')
    myprof = TH1F()
    h.ProjectionX(name+'_myprof').Copy(myprof)
    myprof.SetName(name+'_myprof')
    myprof.SetTitle('sigma, '+h.GetTitle())
    #
    nw = int(sqrt(N)+0.5)
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


def plot_ip(hist, hist_max, filename):
    fits_canvas, hist = make_profile(hist)
    c1 = TCanvas(hist.GetName()+'_c', '', 750, 500)
    hist.SetStats(0)
    hist.SetMinimum(0.)
    hist.SetMaximum(hist_max)
    fun = TF1('pol1', 'pol1')
    hist.Fit(fun)
    a0 = fun.GetParameter(0)*1000.
    a1 = fun.GetParameter(1)*1000.
    txt = '1000*f = {a0:.1f} + {a1:.1f}/pt'.format(a0=a0, a1=a1)
    # txt = 'Sigma='+'%4.1f' % (a0)+'+'+'%4.1f' % (a1)+'/pt'
    tx = TText(0.25, 0.07, txt)
    tx.DrawText(0.25, 0.07, txt)
    c1.Print(filename+'resolution.png')


def plot_split_canv(plot_type, plots):
    assert len(plots) == 6
    split_cav = TCanvas(plot_type+'_split_cav', plot_type, 1200, 800)
    split_cav.Divide(3, 2)
    for i, (hist, title) in enumerate(plots, start=1):
        if hist is not None:
            split_cav.cd(i)
            h = hist.ProjectionY()
            h.SetTitle(plot_type+' '+title)
            print_sigma(h)

    split_cav.Print(plot_type.replace(' ', '_')+'.png')


run_script()
