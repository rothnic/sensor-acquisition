"""
Process communication example

Covers:

- Resources: Store

Scenario:
  This example shows how to interconnect simulation model elements
  together using :class:`~simpy.resources.store.Store` for one-to-one,
  and many-to-one asynchronous processes. For one-to-many a simple
  BroadCastPipe class is constructed from Store.

When Useful:
  When a consumer process does not always wait on a generating process
  and these processes run asynchronously. This example shows how to
  create a buffer and also tell is the consumer process was late
  yielding to the event from a generating process.

  This is also useful when some information needs to be broadcast to
  many receiving processes

  Finally, using pipes can simplify how processes are interconnected to
  each other in a simulation model.

Example By:
  Keith Smith

"""
import random

import simpy


RANDOM_SEED = 42
SIM_TIME = 100


class BroadcastPipe(object):
    """A Broadcast pipe that allows one process to send messages to many.

    This construct is useful when message consumers are running at
    different rates than message generators and provides an event
    buffering to the consuming processes.

    The parameters are used to create a new
    :class:`~simpy.resources.store.Store` instance each time
    :meth:`get_output_conn()` is called.

    """
    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.pipes = []

    def put(self, value):
        """Broadcast a *value* to all receivers."""
        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        events = [store.publish(value) for store in self.pipes]
        return self.env.all_of(events)  # Condition event for all "events"

    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe.

        The return value is a :class:`~simpy.resources.store.Store`.

        """
        pipe = simpy.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe


def missile(name, env, out_pipe, times):
    """A process which randomly generates messages."""
    for time in times:
        # wait for next transmission
        yield env.timeout(1)

        # messages are time stamped to later check if the consumer was
        # late getting them.  Note, using event.triggered to do this may
        # result in failure due to FIFO nature of simulation yields.
        # (i.e. if at the same env.now, message_generator puts a message
        # in the pipe first and then message_consumer gets from pipe,
        # the event.triggered will be True in the other order it will be
        # False
        msg = (env.now, '%s says hello at %d' % (name, env.now))
        out_pipe.publish(msg)


class Sensor(object):

    in_events = ['task']
    out_events = ['detection', 'track_update']

    def __init__(self, name, env, comm):
        self.name = name
        self.detections = [5, 10, 20]
        self.detect_proc = env.process(self.proc_detections(env))
        self.comm_out = comm
        self.comm_in = comm.subscribe()

    def proc_detections(self, env):
        while True:
            msg = yield self.comm_in.get()
            if msg[0] in self.detections:
                msg = ('detection', 'detection at %d' % env.now)
                self.comm_out.publish(msg)


class CommandControl(object):

    in_events = ['detection']

    def __init__(self, name, env, comm):
        self.name = name
        self.track_proc = env.process(self.process_track(env))
        self.comm_out = comm
        self.comm_in = comm.subscribe()

    def process_track(self, env):
        while True:
            msg = yield self.comm_in.get()
            if msg[0] in self.in_events:
                print('detection processed at %d' % env.now)


# Setup and start the simulation
print('Process communication')
random.seed(RANDOM_SEED)
#env = simpy.Environment()
times = range(1, 50)

# For one-to-one or many-to-one type pipes, use Store
# pipe = simpy.Store(env)
# env.process(missile('Generator A', env, pipe, times))
# s1 = Sensor('Consumer A', env, pipe)
# c1 = CommandControl('C2 1', env, pipe)
#
# print('\nOne-to-one pipe communication\n')
# env.run()

# For one-to many use BroadcastPipe
# (Note: could also be used for one-to-one,many-to-one or many-to-many)
env = simpy.Environment()
bc_pipe = BroadcastPipe(env)

for i in range(5):
    env.process(missile('Generator %d' % i, env, bc_pipe, times))
s1 = Sensor('Consumer A', env, bc_pipe)
s2 = Sensor('Consumer B', env, bc_pipe)
c1 = CommandControl('C2 1', env, bc_pipe)

print('\nOne-to-many pipe communication\n')
env.run()