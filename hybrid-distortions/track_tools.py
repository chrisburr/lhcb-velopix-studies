from __future__ import division
from __future__ import print_function

from collections import defaultdict
from math import atan2

import GaudiPython
import ROOT
from LHCbMath import XYZPoint, XYZVector
from LinkerInstances.eventassoc import linkedTo

LHCb = GaudiPython.gbl.LHCb
LineTraj = LHCb.LineTraj
Range = GaudiPython.gbl.std.pair('double', 'double')

# LHCb Tracks appear to have the following states
# > Downstream BegRich2               FirstMeasurement
# > Long       BegRich2 ClosestToBeam FirstMeasurement
# > Ttrack     BegRich2               FirstMeasurement
# > Upstream            ClosestToBeam FirstMeasurement
# > Velo                ClosestToBeam
state_to_use = {
    LHCb.Track.Velo: LHCb.State.ClosestToBeam,
    LHCb.Track.Downstream: LHCb.State.FirstMeasurement,
    LHCb.Track.Long: LHCb.State.FirstMeasurement,
    LHCb.Track.Ttrack: LHCb.State.FirstMeasurement,
    LHCb.Track.Upstream: LHCb.State.FirstMeasurement,
}


def initialise():
    global appMgr, evt, poca, extrap, vertex_fitter
    appMgr = GaudiPython.AppMgr()
    evt = appMgr.evtsvc()
    poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
    extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
    # vertex_fitter = appMgr.toolsvc().create('OfflineVertexFitter', interface='IVertexFit')
    vertex_fitter = appMgr.toolsvc().create('LoKi::VertexFitter', interface='IVertexFit')
    # Because why not...
    ROOT.gSystem.Load('/cvmfs/lhcb.cern.ch/lib/lhcb/LHCB/LHCB_v41r1/InstallArea/x86_64-slc6-gcc49-opt/lib/libLinkerEvent.so')
    run.n = -1
    return appMgr, evt


def run(step=1):
    appMgr.run(1)
    get_clusters.clusters = None
    run.n += 1
    return run.n


def get_clusters():
    # This is very slow so use aggressive caching
    if get_clusters.clusters is None:
        get_clusters.clusters = {
            c.channelID().channelID(): Cluster(c)
            for c in evt['/Event/Raw/VP/Clusters']
        }
    return get_clusters.clusters.copy()


class Cluster(object):
    """docstring for Cluster"""
    def __init__(self, cluster):
        self._cluster = cluster

    @property
    def channel_id(self):
        return self._cluster.channelID().channelID()

    @property
    def x(self):
        return self._cluster.x()

    @property
    def y(self):
        return self._cluster.y()

    @property
    def z(self):
        return self._cluster.z()

    @property
    def position(self):
        return XYZPoint(self.x, self.y, self.z)


class Hit(object):
    """docstring for Hit"""

    def __init__(self, hit, track):
        self._hit = hit
        self._track = track

    @property
    def cluster(self):
        raise NotImplementedError()


class VPHit(Hit):
    """docstring for VPHit"""
    def __init__(self, hit, track):
        super(VPHit, self).__init__(hit, track)
        assert self._hit.isVP()

    @property
    def vp_id(self):
        try:
            return self._vp_id
        except AttributeError:
            self._vp_id = self._hit.vpID()
            return self._vp_id

    @property
    def cluster(self):
        return get_clusters()[self.vp_id.channelID()]

    @property
    def sidepos(self):
        return self.vp_id.sidepos()

    @property
    def module(self):
        return self.vp_id.module()

    @property
    def sensor(self):
        return self.vp_id.sensor()

    @property
    def station(self):
        return self.vp_id.station()

    @property
    def chip(self):
        return self.vp_id.chip()

    @property
    def row(self):
        return self.vp_id.row()

    @property
    def col(self):
        return self.vp_id.col()

    @property
    def scol(self):
        return self.vp_id.scol()


class UTHit(Hit):
    """docstring for UTHit"""
    def __init__(self, hit, track):
        super(UTHit, self).__init__(hit, track)
        assert self._hit.isUT()


class FTHit(Hit):
    """docstring for FTHit"""
    def __init__(self, hit, track):
        super(FTHit, self).__init__(hit, track)
        assert self._hit.isFT()


class Track(object):
    """docstring for Track"""
    def __init__(self, track):
        self._track = track

    def fit_to_point(self, position):
        state = self.state
        assert extrap.propagate(state, position.z())
        traj = LineTraj(state.position(), state.slopes(), Range(-1000., 1000.))
        residual = XYZVector()
        s = ROOT.Double(0.1)
        a = ROOT.Double(0.0005)
        assert poca.minimize(traj, s, position, residual, a)
        return traj.position(s), residual

    @property
    def vp_hits(self):
        return [h for h in self.hits if isinstance(h, VPHit)]

    @property
    def track_type(self):
        return LHCb.Track.TypesToString(self._track.type())

    @property
    def mc_particle(self):
        track_to_mc = linkedTo(LHCb.MCParticle, LHCb.Track, 'Rec/Track/Best')
        if track_to_mc.range(self._track).size() == 1:
            return MCParticle(track_to_mc.first(self._track))
        else:
            raise ValueError('More/less that one MC particle found')

    @property
    def hits(self):
        for hit in self._track.lhcbIDs():
            if hit.isVP():
                yield VPHit(hit, self)
            elif hit.isUT():
                yield UTHit(hit, self)
            elif hit.isFT():
                yield FTHit(hit, self)
            else:
                raise ValueError('Unrecognised hit')

    @property
    def state(self):
        return self._track.stateAt(state_to_use[self._track.type()]).clone()

    @property
    def rx(self):
        slope = self.state.slopes()
        return atan2(slope.x(), slope.z())

    @property
    def ry(self):
        slope = self.state.slopes()
        return atan2(slope.y(), slope.z())

    @property
    def p(self):
        return self._track.p()

    @property
    def pt(self):
        return self._track.pt()

    @property
    def px(self):
        return self._track.momentum().x()

    @property
    def py(self):
        return self._track.momentum().y()

    @property
    def pz(self):
        return self._track.momentum().z()

    @property
    def key(self):
        return self._track.key()


class MCParticle(object):
    """docstring for MCParticle"""
    def __init__(self, mc_particle):
        self._mc_particle = mc_particle

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._mc_particle == other._mc_particle
        return False

    @property
    def px(self):
        return self._mc_particle.momentum().x()

    @property
    def py(self):
        return self._mc_particle.momentum().y()

    @property
    def pz(self):
        return self._mc_particle.momentum().z()

    @property
    def pid(self):
        return self._mc_particle.particleID().pid()

    @property
    def mother(self):
        mother = self._mc_particle.mother()
        if mother:
            return MCParticle(mother)
        else:
            raise ValueError('No mother found')

    @property
    def origin_vertex(self):
        return self._mc_particle.originVertex().position()

    @property
    def end_vertices(self):
        return [v.target().position() for v in self._mc_particle.endVertices()]


def fit_vertex(kp_track, km_track, pi_track):
    pi, kp, km = None, None, None
    for p in evt['Phys/PreLoadPions/Particles']:
        if p.proto().track().key() == pi_track.key:
            pi = p

    for p in evt['Phys/PreLoadKaons/Particles']:
        if p.proto().track().key() == kp_track.key:
            kp = p
        if p.proto().track().key() == km_track.key:
            km = p

    if kp is None or km is None:
        raise ValueError('Failed to find tracks')

    d0_vertex = LHCb.Vertex()
    D0 = LHCb.Particle(LHCb.ParticleID(421))
    vertex_fitter.fit(kp, km, d0_vertex, D0)

    true_d0_vertex = kp_track.mc_particle.origin_vertex
    true_dst_vertex = pi_track.mc_particle.origin_vertex

    true = true_d0_vertex - true_dst_vertex
    fitted = d0_vertex.position() - true_d0_vertex

    return D0, d0_vertex, true_d0_vertex, true_dst_vertex, true, fitted, kp, km, pi


def get_dstars():
    particles = defaultdict(list)
    for i, track in enumerate(map(Track, evt['Rec/Track/Best'])):
        try:
            if track.mc_particle.mother.pid in [421, -421, 413, -413]:
                particles[track.mc_particle.pid].append(track)
        except ValueError:
            pass

    valid_d0s = []
    for kp in particles[321]:
        for km in particles[-321]:
            if kp.mc_particle.mother == km.mc_particle.mother:
                valid_d0s.append([kp, km])

    valid_dsts = []
    for pi in particles[211]+particles[-211]:
        for kp, km in valid_d0s:
            if kp.mc_particle.mother.mother == pi.mc_particle.mother:
                assert km.mc_particle.mother.mother == pi.mc_particle.mother
                valid_dsts.append([kp, km, pi])

    return valid_dsts
