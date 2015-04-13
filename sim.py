__author__ = 'nickroth'

import random
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import simpy

from sensor import Sensor
from missile import Missile
from sim_utils import EventBroker

MAX_TIME = 100


def run_sim():
    # Create the environment (event-based simulation driver)
    env = simpy.Environment()

    # Create a pub/sub event broker for all components to communicate over
    bc_pipe = EventBroker(env)

    # Create 2 sensors
    sensor1 = Sensor('Sensor A', env, bc_pipe)
    sensor2 = Sensor('Sensor B', env, bc_pipe)

    # Create 10 missiles, each with different initial/end times
    missiles_list = []
    for i in range(10):
        times = range(random.randrange(0, 20), random.randrange(50, MAX_TIME))
        missiles_list.append(Missile(name='Missile %d' % i, env=env, comm=bc_pipe, times=times))

    # Run the simulation until
    env.run(until=MAX_TIME)

    return sensor1, sensor2, missiles_list


def plot_acquisition(sensors, missiles):
    # Distribution of search
    plt.figure(0)
    plt.subplot2grid((2, 2), (0, 0))
    sns.distplot(sensors[0].beam_time, axlabel='Times Where Beam Resources Used for Search',
                 label=get_search_text(sensors[0]))
    sns.distplot(sensors[1].beam_time, axlabel='Times Where Beam Resources Used for Search',
                 label=get_search_text(sensors[1]))
    plt.legend()

    # Plot search locations versus time
    ax2 = plt.subplot2grid((2, 2), (0, 1))

    ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
    ax2.scatter(sensors[0].beam_time, sensors[0].beam_history, label=sensors[0].id + ' Search Beams',
                c='b', zorder=3)
    ax2.scatter(sensors[1].beam_time, sensors[1].beam_history, label=sensors[1].id + ' Search Beams',
                c='g', zorder=3)

    # Add missile locations to search history over time
    for missile in missiles:

        # Plot the missile locations in truth
        missile_line, = ax2.plot(missile.times, missile.position, label='missile %s'.join([str(missile.id)]), zorder=1)

        # Loop over the sensors
        for sen in sensors:

            # Find the missile tracks for the sensor
            if missile.id in sen.track_data.keys():
                # Use the logged track times to get the corresponding position
                track = sen.track_data[missile.id]
                track_df = pd.DataFrame(data={'time': track.time, 'quality': track.quality})
                missile_df = pd.DataFrame(data={'time': missile.times, 'position': missile.position})

                missile_df2 = missile_df.loc[(missile_df.time > min(track_df.time)) & (missile_df.time < max(
                    track_df.time))]

                # Plot the track points
                ax2.scatter(missile_df2.time, missile_df2.position, c='r', zorder=2)
                ax3.plot(track_df.time, track_df.quality, c=missile_line.get_color(), label=''.join([missile.id, ':',
                                                                                                     sen.id]))

    ax2.legend()
    ax3.legend()
    ax2.set_xlabel('Simulation Time')
    ax2.set_ylabel('Notional Position')
    ax3.set_xlabel('Simulation Time')
    ax3.set_ylabel('Notional Track Quality')
    plt.show()


def get_search_text(sensor):
    beams = sensor.beams_locations
    search_width = max(beams) - min(beams)
    txt = ''.join([sensor.id, ' (search width = ', str(search_width)])
    return txt

if __name__ == '__main__':

    # Run simulation, retrieve simulated components
    s1, s2, missiles = run_sim()

    # Plot stats from the simulated components
    plot_acquisition((s1, s2), missiles)