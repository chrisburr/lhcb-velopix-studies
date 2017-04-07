from __future__ import division
from __future__ import print_function

from collections import defaultdict
from math import atan2, sqrt

import GaudiPython
import ROOT
from LHCbMath import XYZPoint, XYZVector
import LoKiAlgo.decorators
from LoKiPhys.decorators import VIPCHI2
from LinkerInstances.eventassoc import linkedTo
GaudiPython.loaddict('libLinkerEvent')

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


class cached_property(object):
    """Descriptor (non-data) for building an attribute on-demand on first use.

    Taken from: http://stackoverflow.com/a/4037979/2685230
    """
    def __init__(self, factory):
        """
        <factory> is called such: factory(instance) to build the attribute.
        """
        self._attr_name = factory.__name__
        self._factory = factory

    def __get__(self, instance, owner):
        # Build the attribute.
        attr = self._factory(instance)

        # Cache the value; hide ourselves.
        setattr(instance, self._attr_name, attr)

        return attr


def initialise():
    global appMgr, evt, poca, extrap, vertex_fitter, loki_algo
    appMgr = GaudiPython.AppMgr()
    evt = appMgr.evtsvc()
    poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
    extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
    # vertex_fitter = appMgr.toolsvc().create('OfflineVertexFitter', interface='IVertexFit')
    vertex_fitter = appMgr.toolsvc().create('LoKi::VertexFitter', interface='IVertexFit')
    run.n = -1
    loki_algo = LoKiAlgo.decorators.Algo('loki_algo')
    return appMgr, evt


def run(step=1):
    appMgr.run(1)
    get_clusters.clusters = None
    get_pvs.pvs = None
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


def get_pvs():
    # This is very slow so use aggressive caching
    if get_pvs.pvs is None:
        get_pvs.pvs = list(evt['/Event/Rec/Vertex/Primary'])
    return list(get_pvs.pvs)


class Cluster(object):
    """docstring for Cluster"""
    def __init__(self, cluster):
        self._cluster = cluster

    @cached_property
    def channel_id(self):
        return self._cluster.channelID().channelID()

    @cached_property
    def x(self):
        return self._cluster.x()

    @cached_property
    def y(self):
        return self._cluster.y()

    @cached_property
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

    @cached_property
    def vp_id(self):
        try:
            return self._vp_id
        except AttributeError:
            self._vp_id = self._hit.vpID()
            return self._vp_id

    @cached_property
    def cluster(self):
        return get_clusters()[self.vp_id.channelID()]

    @cached_property
    def sidepos(self):
        return self.vp_id.sidepos()

    @cached_property
    def module(self):
        return self.vp_id.module()

    @cached_property
    def sensor(self):
        return self.vp_id.sensor()

    @cached_property
    def station(self):
        return self.vp_id.station()

    @cached_property
    def chip(self):
        return self.vp_id.chip()

    @cached_property
    def row(self):
        return self.vp_id.row()

    @cached_property
    def col(self):
        return self.vp_id.col()

    @cached_property
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

    def fit_to_point(self, position, minimise=True):
        state = self.state
        assert extrap.propagate(state, position.z())
        if minimise:
            traj = LineTraj(state.position(), state.slopes(), Range(-1000., 1000.))
            residual = XYZVector()
            s = ROOT.Double(0.1)
            a = ROOT.Double(0.0005)
            assert poca.minimize(traj, s, position, residual, a)
            return traj.position(s), residual
        else:
            return state.position()

    @property
    def vp_hits(self):
        return [h for h in self.hits if isinstance(h, VPHit)]

    @cached_property
    def track_type(self):
        return LHCb.Track.TypesToString(self._track.type())

    @cached_property
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

    @cached_property
    def rx(self):
        slope = self.state.slopes()
        return atan2(slope.x(), slope.z())

    @cached_property
    def ry(self):
        slope = self.state.slopes()
        return atan2(slope.y(), slope.z())

    @cached_property
    def p(self):
        return self._track.p()

    @cached_property
    def pt(self):
        return self._track.pt()

    @cached_property
    def px(self):
        return self._track.momentum().x()

    @cached_property
    def py(self):
        return self._track.momentum().y()

    @cached_property
    def pz(self):
        return self._track.momentum().z()

    @cached_property
    def key(self):
        return self._track.key()

    @cached_property
    def ip(self):
        # Find the PV
        best_distance = 1e1000
        best_pv = None
        for pv in get_pvs():
            state = self.state
            assert extrap.propagate(state, pv.position().z())
            dist = sqrt(
                (state.x() - pv.position().x())**2 +
                (state.y() - pv.position().y())**2
            )
            if dist < best_distance:
                best_distance = dist
                best_pv = pv
        assert best_pv

        first_state = self._track.firstState()
        true_origin = best_pv.position()
        # Here I use TrackParabolicExtrapolator instead of
        # CubicStateInterpolationTraj
        assert extrap.propagate(first_state, true_origin.z())
        tx = first_state.tx()
        ty = first_state.ty()
        IPx = first_state.x() - true_origin.x()
        IPy = first_state.y() - true_origin.y()
        IP3D = sqrt((IPx*IPx + IPy*IPy) / (1 + tx*tx + ty*ty))
        return IP3D, IPx, IPy


class MCParticle(object):
    """docstring for MCParticle"""
    def __init__(self, mc_particle):
        self._mc_particle = mc_particle

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._mc_particle == other._mc_particle
        return False

    @cached_property
    def px(self):
        return self._mc_particle.momentum().x()

    @cached_property
    def py(self):
        return self._mc_particle.momentum().y()

    @cached_property
    def pz(self):
        return self._mc_particle.momentum().z()

    @cached_property
    def pid(self):
        return self._mc_particle.particleID().pid()

    @cached_property
    def mother(self):
        mother = self._mc_particle.mother()
        if mother:
            return MCParticle(mother)
        else:
            raise ValueError('No mother found')

    @cached_property
    def origin_vertex(self):
        return self._mc_particle.originVertex().position()

    @cached_property
    def end_vertices(self):
        return [v.target().position() for v in self._mc_particle.endVertices()]


def fit_vertex(kp_track, km_track, pi_track):
    pi, kp, km = None, None, None
    for p in evt['Phys/PreLoadPions/Particles']:
        if p.proto().track().key() == pi_track.key:
            pi = p

    for p in evt['Phys/PreLoadKaons/Particles']:
        p_key = p.proto().track().key()
        if p_key == kp_track.key:
            kp = p
        elif p_key == km_track.key:
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

    best_chi2 = 1e1000
    best_pv = None
    func = VIPCHI2(D0, loki_algo.geo())
    for pv in get_pvs():
        chi2 = func(pv)
        if best_chi2 > chi2:
            best_chi2 = chi2
            best_pv = pv

    return D0, best_pv, best_chi2, d0_vertex, true_d0_vertex, true_dst_vertex, true, fitted, kp, km, pi


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
