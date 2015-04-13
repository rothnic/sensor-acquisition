__author__ = 'nickroth'

import simpy
import numpy as np
import random


class Sensor(object):
    def __init__(self, name, env, comm):
        self.id = name
        self.beams = simpy.PriorityResource(env, capacity=4)
        self.tracks = {}
        self.track_data = {}
        self.comm_out = comm
        self.comm_in = comm.subscribe(topic='THREAT_POSITION')
        self.truth_proc = env.process(self.truth_processor())
        self.detector_proc = env.process(self.detector())
        self.env = env
        self.position_update = env.event()
        self.beam_hit = env.event()
        self.prev_message = {}
        self.current_message = {}
        self.beam_history = []
        self.beam_time = []

        min_fence = random.randrange(190, 210)
        max_fence = random.randrange(215, 235)
        self.beams_locations = np.linspace(min_fence, max_fence, (max_fence-min_fence)/1)
        self.beam_search = [env.process(self.search(loc)) for loc in self.beams_locations]

    def truth_processor(self):
        """
        Get each message available, store last and current message in object for child processes
        :return:
        """
        while True:
            msg = yield self.comm_in.next()
            if msg.origin_id in self.current_message.keys():
                self.prev_message[msg.origin_id] = self.current_message[msg.origin_id]
            else:
                self.prev_message[msg.origin_id] = None

            self.current_message[msg.origin_id] = msg
            self.position_update.succeed(value=msg.origin_id)
            self.position_update = self.env.event()

    def search(self, location):
        """
        Resource constrained process to search a volume for a contained object.
        :return:
        """
        serv_time = 0.1

        # Continually search by requesting beam resources and logging when we search the location
        while True:
            request = self.beams.request(priority=5)
            yield request
            yield self.env.timeout(serv_time)
            self.beams.release(request)
            self.beam_history.append(location)
            self.beam_time.append(self.env.now)

    def detector(self):
        while True:
            missile_id = yield self.position_update
            now = self.current_message[missile_id]
            last = self.prev_message[missile_id]

            if self.in_fov(now.value):
                print('%s in fov of %s' % (now.origin_id, self.id))

                intersect = False
                for beam_pos, time in zip(self.beam_history, self.beam_time):
                    if last.time < time <= now.time:
                        if np.absolute(beam_pos - now.value) < 1.0:
                            print('intersect')
                            intersect = True

                if intersect:
                    x = np.random.beta(2, 2)
                    if x > 0.5:
                        print('%s detected %s' % (self.id, now.origin_id))
                        if now.origin_id not in self.tracks.keys():
                            self.tracks[now.origin_id] = self.env.process(self.tracker(Track(now.origin_id,
                                                                                             self.env)))

    def tracker(self, track):
        print('starting track for %s' % track.missile_id)

        # tracker process runs for life of a track, which ends when exiting the sensor FOV
        while self.in_fov(self.current_message[track.missile_id].value):

            # Request beams from the shared beam resource with high priority
            request = self.beams.request(priority=1)
            yield request

            # At this point, the request was successful. A timeout means that we use the resource for this time
            yield self.env.timeout(1)

            # Now we can release the resource now that we are done with it
            self.beams.release(request)

            # Update and store the quality of the track for the current time
            track.update(np.random.beta(2.0, 3.0))

            print('track quality for %s is %f' % (track.missile_id, track.init_quality))
            yield self.env.timeout(0.1)

        # When track ends, store the final track based on missile id
        self.track_data[track.missile_id] = track

    @staticmethod
    def in_fov(position):
        if 200 < position < 500:
            return True
        else:
            return False


class Track(object):
    def __init__(self, missile_id, env):
        self.missile_id = missile_id
        self.env = env
        self.init_quality = 0.0
        self.quality = []
        self.time = []

    def update(self, quality_change):
        self.init_quality += quality_change
        self.time.append(self.env.now)
        self.quality.append(self.init_quality)