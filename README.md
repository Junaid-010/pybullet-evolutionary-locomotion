# Evolving Creature Morphologies & Locomotion in PyBullet

This project uses Genetic Algorithms (GAs) inside the PyBullet physics engine to evolve 3D virtual creatures capable of climbing steep, uneven terrain.

Locomotion on flat ground is relatively straightforward, but climbing a non-linear Gaussian mountain introduced severe physical hurdles: creatures easily lost friction, tipped over, or slid back down. To solve this, the project expands standard GAs beyond simple motor tuning by evolving both the physical body (morphology) and the motor timing (phase shifts) simultaneously.

---

## What the System Does

1. Morphological Evolution (Cylinders vs. Boxes):
Standard setups typically use cylindrical or capsule links. On an incline, cylinders tend to roll downhill continuously. The genome was modified to allow links to evolve into either cylinders or boxes via dynamic URDF generation. Box-shaped links naturally provide flat contact surfaces, using passive friction to stabilize the body against gravity without requiring complex active balancing.


2. Gait Coordination (Phase Offsets & Joint Limits):
Early generations moved limbs synchronously, essentially hopping or flailing without making progress. Adding a `control-phase-offset` gene enabled limb movements to stagger, giving rise to alternating reach-and-pull gaits (stepping with one side while anchoring with the other). Joint upper and lower limits were also evolved to prevent unnatural 360-degree joint rotations and create rigid, weight-bearing structures.


3. Hybrid Fitness Function:
A simple distance-from-start metric often caused creatures to exploit local minima—like running away from the mountain across the flat floor. The fitness function was rewritten to balance four signals:


* Forward Movement (Y-axis): Encourages moving toward the base of the mountain.


. Height Gain (Z-axis): Strongly weighted to prioritize climbing over flat-ground movement.


. Peak Centering: Draws the agent toward the center coordinate of the peak.


. Movement Bonus: Rewards overall displacement to discourage passive resting.





$$\text{Fitness} = \max(\Delta y, 0) \times 3.5 + \max(\Delta z, 0) \times 4.0 + (\text{dist}_{\text{start\_center}} - \text{dist}_{\text{end\_center}}) \times 2.5 + \text{total\_dist} \times 0.4$$


---

## Evolutionary Observations

. Generations 0–50: Random limb mixtures. Cylindrical creatures flailed in place or rolled back to the floor with low fitness scores.


. Generations 50–200: Selective pressure rapidly favored box-shaped lower links. Elite creatures began to resemble low sleds or tables that slid smoothly on flat surfaces without rolling.


. Generations 200–1000: Phase offsets evolved, unlocking coordinated, alternating gaits where one limb held the slope while another reached upward.


. Size Convergence: Creatures naturally converged around 5 to 6 links. Smaller creatures (2–3 links) lacked leverage, while larger ones (10+ links) were too heavy for the simulation's motor force limits.



---

## File Overview

. `creature.py`: Builds creature bodies, manages motor control, computes fitness, and generates URDF XML tags.


. `genome.py`: Defines the gene specifications (link shapes, motor frequencies, phase offsets, joint limits).


. `simulation.py`: Sets up the PyBullet physics world, gravity, stepping, and contact tracking.


. `cw_envt_copy.py`: Generates the Gaussian mountain terrain mesh inside the arena.


. `test_ga_no_threads.py`: Main GA loop managing populations, mutations, evaluations, and telemetry logging.



---

## Setup & Running

Clone the repository and install the dependencies:

```bash
git clone https://github.com/Junaid-010/pybullet-evolutionary-locomotion.git
cd pybullet-evolutionary-locomotion

python3 -m venv venv
source venv/bin/activate
pip install pybullet numpy matplotlib

```

To run the genetic algorithm across generations:

```bash
python test_ga_no_threads.py

```

To view a saved run or telemetry in real time:

```bash
python realtime_from_csv.py

```