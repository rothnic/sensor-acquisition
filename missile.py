__author__ = 'nickroth'

import numpy as np
from sim_utils import SimEvent


class Missile(object):
    def __init__(self, name, env, comm, times):
        self.id = name
        self.env = env
        self.comm_out = comm
        self.times = times
        self.position = np.linspace(100, 1000, num=len(times))
        self.propagate_process = env.process(self.propagate())

    def propagate(self):
        # wait until first time to start yielding position
        yield self.env.timeout(self.times[0])
        print('%s is launching at %d' % (self.id, self.env.now))

        for idx, time in enumerate(self.times):
            pos = self.position[idx]
            print('%s position event for t=%d at position=%d' % (self.id, self.env.now, pos))
            msg = SimEvent(origin_id=self.id, time=self.env.now, event='THREAT_POSITION', value=pos)
            self.publish(msg)
            yield self.env.timeout(1)

    def publish(self, msg):
        self.comm_out.publish(topic='THREAT_POSITION', msg=msg)