from __future__ import division
from __future__ import print_function

from math import atan2

import GaudiPython
import ROOT
from LHCbMath import XYZPoint, XYZVector
from LinkerInstances.eventassoc import linkedTo

LineTraj = GaudiPython.gbl.LHCb.LineTraj
Range = GaudiPython.gbl.std.pair('double', 'double')

# LHCb Tracks appear to have the following states
# > Downstream BegRich2               FirstMeasurement
# > Long       BegRich2 ClosestToBeam FirstMeasurement
# > Ttrack     BegRich2               FirstMeasurement
# > Upstream            ClosestToBeam FirstMeasurement
# > Velo                ClosestToBeam
state_to_use = {
    ROOT.LHCb.Track.Velo: ROOT.LHCb.State.ClosestToBeam,
    ROOT.LHCb.Track.Downstream: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Long: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Ttrack: ROOT.LHCb.State.FirstMeasurement,
    ROOT.LHCb.Track.Upstream: ROOT.LHCb.State.FirstMeasurement,
}


def initialise():
    global appMgr, evt, poca, extrap
    appMgr = GaudiPython.AppMgr()
    evt = appMgr.evtsvc()
    poca = appMgr.toolsvc().create('TrajPoca', interface='ITrajPoca')
    extrap = appMgr.toolsvc().create('TrackParabolicExtrapolator', interface='ITrackExtrapolator')
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
    def x(self):
        return self._cluster.x()

    @property
    def y(self):
        return self._cluster.y()

    @property
    def z(self):
        return self._cluster.z()

    @property
    def point(self):
        return XYZPoint(self.x, self.y, self.z)


class Hit(object):
    """docstring for Hit"""

    def __init__(self, hit, track):
        self._hit = hit
        self._track = track

    @property
    def cluster(self):
        raise NotImplementedError()

    def fit(self):
        state = self._track.state
        assert extrap.propagate(state, self.cluster.z)
        traj = LineTraj(state.position(), state.slopes(), Range(-1000., 1000.))
        residual = XYZVector()
        s = ROOT.Double(0.1)
        a = ROOT.Double(0.0005)
        assert poca.minimize(traj, s, self.cluster.point, residual, a)
        return residual, traj.position(s)

    @property
    def residual(self):
        residual, position = self.fit()
        return residual

    @property
    def closest_point(self):
        residual, position = self.fit()
        return position


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

    @property
    def vp_hits(self):
        return [h for h in self.hits if isinstance(h, VPHit)]

    @property
    def track_type(self):
        return ROOT.LHCb.Track.TypesToString(self._track.type())

    @property
    def mc_particle(self):
        MCParticle = GaudiPython.gbl.LHCb.MCParticle
        track_to_mc = linkedTo(MCParticle, Track, 'Rec/Track/Best')
        assert track_to_mc.range(self._track).size() == 1
        return track_to_mc.first(self._track)

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


class MCParticle(object):
    """docstring for MCParticle"""
    def __init__(self, mc_particle):
        self._mc_particle = mc_particle
