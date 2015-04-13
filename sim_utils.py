__author__ = 'nickroth'

import simpy


class EventListener(object):
    def __init__(self, env, comm):
        self.env = env


class SimEvent(object):
    def __init__(self, origin_id, time, event, value=None):
        self.origin_id = origin_id
        self.time = time
        self.event = event
        self.value = value


class EventBroker(object):
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
        self.topics = {}

    def publish(self, topic, msg):
        """Broadcast a *value* to all receivers."""
        if not self.topics:
            raise RuntimeError('There are no output pipes.')
        events = [sub.publish(msg) for sub in self.topics[topic]]
        return self.env.all_of(events)  # Condition event for all "events"

    def subscribe(self, topic='global'):
        """Get a new output connection for this broadcast pipe.

        The return value is a :class:`~sim_utils.Subscription`.

        """
        sub = Subscription(self.env, topic=topic, capacity=self.capacity)

        # add topic if it doesn't exist
        if topic not in self.topics.keys():
            self.topics[topic] = []

        topic_store = self.topics[topic]
        topic_store.append(sub)
        return sub


class Subscription(object):
    def __init__(self, env, topic='default', capacity=simpy.core.Infinity):
        self.topic = topic
        self.topic_buffer = simpy.Store(env, capacity=capacity)

    def publish(self, msg):
        """ Delivers the provided message to the subscription.

        :param msg: any data type
        :return: None
        """
        return self.topic_buffer.put(msg)

    def next(self):
        """ Get the next message from the subscription, when a message is available.

        :return: the message that was published
        """
        return self.topic_buffer.get()


class Consumer(object):
    def __init__(self, eb, env, topic):
        self.eb = eb
        self.sub = self.eb.subscribe(topic=topic)
        self.con_proc = env.process(self.proc_messages())

    def proc_messages(self):
        while True:
            msg = yield self.sub.next()
            print(msg)


class MissileTruth(object):
    def __init__(self, comm, ):
        pass


def truth_processor(self):
    """
    Get each message available, store last and current message in object for child processes
    :return:
    """
    while True:
        msg = yield self.comm_in.get()
        if msg.origin_id in self.current_message.keys():
            self.prev_message[msg.origin_id] = self.current_message[msg.origin_id]
        else:
            self.prev_message[msg.origin_id] = None

        self.current_message[msg.origin_id] = msg
        self.position_update.succeed(value=msg.origin_id)
        self.position_update = self.env.event()


if __name__ == '__main__':
    environ = simpy.Environment()
    eb = EventBroker(environ)

    con = Consumer(eb, environ, topic='STATUS')
    eb.publish(topic='STATUS', msg='Active')
    eb.publish(topic='STATUS', msg='Down')
    eb.publish(topic='STATUS', msg='Active')

    environ.run()