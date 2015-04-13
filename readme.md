Event-Driven Sensor Acquisition Model
---
A simple example for how you could model the resources of multiple sensors viewing multiple missiles, where each sensor has a prioritized set of tasks to track and acquire the missiles (in order of importance). This simulation is entirely abstract, implementing only the reactive behaviors of the systems and no representation of electromagnetics or rocket motor thrust.

The natural challenge occurs when the resources available are all consumed by tracking and you can no longer acquire, which then slows down the searching activity, resulting in missed acquisitions in some cases.

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
