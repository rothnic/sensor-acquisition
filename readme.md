Event-Driven Sensor Acquisition Model
---
A simple example for how you could model the resources of multiple sensors viewing multiple missiles, where each sensor has a prioritized set of tasks to track and acquire the missiles (in order of importance). This simulation is entirely abstract, implementing only the reactive behaviors of the systems and no representation of electromagnetics or rocket motor thrust.

The natural challenge occurs when the resources available are all consumed by tracking and you can no longer acquire, which then slows down the searching activity, resulting in missed acquisitions in some cases. You can see this concept play out in the following plots produced by the simulation:

![Plots](http://i.imgur.com/zgcFFwa.png)
**Upper Left** - Histogram of beams being used for search (instead of tracking) for each sensor. Notice the dip is searching at the same time where the red dots in the Upper Right plot appear.

**Upper Right** - Shows the notional movement of the missiles, and (in red) where they are tracked. Notice that they can track for much longer than they acquire via a pre-defined search sector. The green/blue dots are when each sensor's scanning of its respective search sector. Notice, they partially overlap, causing the resulting difference in loading times. This is an initial attempt to simulate missiles entering in the field of view at different instances in time relative to each sensor.

**Lower** - A notional `track quality`, that increases each time there is a track update, for each sensor/acquired missile pairing.

If you zoom into the plot in the upper right, you see this:
![Zoom of Scanning](http://i.imgur.com/O89Zt8D.png)
This shows the search scanning slowing down as more and more of the missiles are being tracked. You can see how there are instances where missiles that cross the field of view during this period can end up not being acquired at all.

This is a very basic start for developing a simulation to test out different task management algorithms, based on a set of constraints imposed by the sensors that are being controlled. All spatial and physics-based aspects have been simplified so that only a distance-like, single dimension is being used.

##Models

###Radar
The radar has a finite number of beams, which it can dwell on a space with for a given amount of time. These are used differently for tracking and acquisition. The search/tracking tasks request resources from the beam scheduler as needed, and with a priority. If too much tracking is going on, then the search tasks will be delayed.
* Search
* Tracking
* Beams/Beam Scheduler
* Search Fence

###Missile
The missile model is very simple, as the purpose isn't to actual develop a physics-based model. We just want a missile that moves at some rate, which the radar can try to see.
* Velocity

##Simulation
The sim is event-driven, meaning that it could be described as "agent-based." The models are added to an environment, being connected through an `EventBroker`. This `EventBroker` provides channels for the models to communicate their events. The simulation is driven by the missiles reporting their position, then the sensors reacting to that position.

The simulation script adds the models and executes the model environment. It collects information about the simulation, then plots it using seaborn.

##Dependencies
Developed using Python 2.7. Requires the following libraries:
* simpy
* numpy
* pandas
* seaborn
* matplotlib

##Running
```
python sim.py
```
