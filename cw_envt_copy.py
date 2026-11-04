# cw_envt_copy.py
import time
import numpy as np
import random
import math
import os
import csv
import sys

try:
    import pybullet as p
    import pybullet_data
    import creature
    import genome
except ImportError as e:
    print(f"CRITICAL ERROR: Missing required module: {e}")
    print("Please ensure pybullet is installed.")
    sys.exit(1)

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setAdditionalSearchPath('shapes/')

p.setGravity(0, 0, -10)

def make_arena(arena_size=50, wall_height=1):
    wall_thickness = 0.5
    floor_collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size / 2, arena_size / 2, wall_thickness],
    )
    floor_visual_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size / 2, arena_size / 2, wall_thickness],
        rgbaColor=[1, 1, 0, 1],
    )
    floor_body = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=floor_collision_shape,
        baseVisualShapeIndex=floor_visual_shape,
        basePosition=[0, 0, -wall_thickness],
    )

    # North and South walls
    wall_collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2],
    )
    wall_visual_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[arena_size / 2, wall_thickness / 2, wall_height / 2],
        rgbaColor=[0.7, 0.7, 0.7, 1],
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape,
        baseVisualShapeIndex=wall_visual_shape,
        basePosition=[0, arena_size / 2, wall_height / 2],
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape,
        baseVisualShapeIndex=wall_visual_shape,
        basePosition=[0, -arena_size / 2, wall_height / 2],
    )

    # East and West walls
    wall_collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2],
    )
    wall_visual_shape = p.createVisualShape(
        shapeType=p.GEOM_BOX,
        halfExtents=[wall_thickness / 2, arena_size / 2, wall_height / 2],
        rgbaColor=[0.7, 0.7, 0.7, 1],
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape,
        baseVisualShapeIndex=wall_visual_shape,
        basePosition=[arena_size / 2, 0, wall_height / 2],
    )
    p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=wall_collision_shape,
        baseVisualShapeIndex=wall_visual_shape,
        basePosition=[-arena_size / 2, 0, wall_height / 2],
    )

# Creating arena
arena_size = 50
make_arena(arena_size=arena_size)

# Loading different terrains from shapes folder
mountain_position = (0, 0, -1)
mountain_orientation = p.getQuaternionFromEuler((0, 0, 0))
mountain = p.loadURDF("gaussian_pyramid.urdf", mountain_position, mountain_orientation, useFixedBase=1)

# Handling elite creature loading with error checking
elite_file = "elite_creatures/elite_1.csv"
if os.path.exists(elite_file):
    try:
        dna = genome.Genome.from_csv(elite_file)
        cr = creature.Creature(gene_count=len(dna))
        cr.update_dna(dna)
        print(f"Loaded elite creature from {elite_file}")
    except Exception as e:
        print(f"Error loading elite creature: {e}. Creating random creature.")
        cr = creature.Creature(gene_count=3)
else:
    print("No elite creature found. Creating random creature.")
    cr = creature.Creature(gene_count=3)

# Generating and saving creature XML
with open("test.urdf", "w") as f:
    f.write(cr.to_xml())

# Loading creature into simulation 
rob1 = p.loadURDF("test.urdf", (0, 0, 10))

# Getting motors
motors = cr.get_motors()


print("Simulation running... Press Ctrl+C to stop.")
print(f"Creature height fitness: {cr.get_current_height()}")
step = 0

try:
    while True:
        p.stepSimulation()
        
        # Getting creature position
        new_pos, orn = p.getBasePositionAndOrientation(rob1)
        cr.update_position(new_pos)
        
        
        # Updating motors every 24 steps 
        if step % 24 == 0:
            for jid in range(p.getNumJoints(rob1)):
                if jid < len(motors):
                    m = motors[jid]
                    p.setJointMotorControl2(
                        rob1, 
                        jid, 
                        controlMode=p.VELOCITY_CONTROL, 
                        targetVelocity=m.get_output(), 
                        force=10
                    )
        
        # Printing fitness every 240 steps 
        if step % 240 == 0:
            height = cr.get_current_height()
            print(f"Step {step//240}s: Height fitness = {height:.3f}")
        
        step += 1
        time.sleep(1.0 / 240.0)
        
except KeyboardInterrupt:
    print("\nSimulation stopped by user.")
    final_height = cr.get_current_height()
    print(f"Final creature height fitness: {final_height:.3f}")