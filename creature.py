import genome 
from xml.dom.minidom import getDOMImplementation
from enum import Enum
import numpy as np

class MotorType(Enum):
    PULSE = 1
    SINE = 2

class Motor:
    def __init__(self, control_waveform, control_amp, control_freq):
        if control_waveform <= 0.5:
            self.motor_type = MotorType.PULSE
        else:
            self.motor_type = MotorType.SINE
        # Minimum values for stability
        self.amp = max(control_amp, 0.15) 
        self.freq = max(control_freq, 0.6)
        self.phase = 0
    
    def get_output(self):
        self.phase = (self.phase + self.freq) % (np.pi * 2)
        if self.motor_type == MotorType.PULSE:
            output = 1 if self.phase < np.pi else -1
        elif self.motor_type == MotorType.SINE:
            output = np.sin(self.phase)
        else:
            output = 0
        return np.clip(output * self.amp, -1.0, 1.0)

class Creature:
    def __init__(self, gene_count):
        self.spec = genome.Genome.get_gene_spec()
        self.dna = genome.Genome.get_random_genome(len(self.spec), gene_count)
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None

    def get_flat_links(self):
        if self.flat_links is None:
            gdicts = genome.Genome.get_genome_dicts(self.dna, self.spec)
            self.flat_links = genome.Genome.genome_to_links(gdicts)
        return self.flat_links
    
    def get_expanded_links(self):
        self.get_flat_links()
        if self.exp_links is not None:
            return self.exp_links
        
        exp_links = [self.flat_links[0]]
        genome.Genome.expandLinks(self.flat_links[0], 
                                  self.flat_links[0].name, 
                                  self.flat_links, 
                                  exp_links)
        self.exp_links = exp_links
        return self.exp_links

    def to_xml(self):
        self.get_expanded_links()
        domimpl = getDOMImplementation()
        adom = domimpl.createDocument(None, "start", None)
        robot_tag = adom.createElement("robot")
        for link in self.exp_links:
            robot_tag.appendChild(link.to_link_element(adom))
        first = True
        for link in self.exp_links:
            if first:
                first = False
                continue
            robot_tag.appendChild(link.to_joint_element(adom))
        robot_tag.setAttribute("name", "pepe")
        return '<?xml version="1.0"?>' + robot_tag.toprettyxml()

    def get_motors(self):
        self.get_expanded_links()
        if self.motors is None:
            motors = []
            for i in range(1, len(self.exp_links)):
                l = self.exp_links[i]
                m = Motor(l.control_waveform, l.control_amp, l.control_freq)
                motors.append(m)
            self.motors = motors 
        return self.motors 
    
    def update_position(self, pos):
        if self.start_position is None:
            self.start_position = pos
        else:
            self.last_position = pos

    def get_distance_travelled(self):
        if self.start_position is None or self.last_position is None:
            return 0
        p1 = np.asarray(self.start_position)
        p2 = np.asarray(self.last_position)
        dist = np.linalg.norm(p1 - p2)
        return dist 

    def get_distance_climbed_y(self):
        if self.start_position is None or self.last_position is None:
            return 0
        y_gain = self.last_position[1] - self.start_position[1]
        z_gain = self.last_position[2] - self.start_position[2]
        return max(y_gain + z_gain, 0)

    # HYBRID FITNESS — encourages forward walking and climbing -- New Fitness function
    def new_fitness(self):
        if self.start_position is None or self.last_position is None:
            return 0.0

        start_x, start_y, start_z = self.start_position
        end_x, end_y, end_z = self.last_position

        # Forward movement toward mountain
        forward_reward = max(end_y - start_y, 0) * 3.5

        # Height gain
        height_reward = max(end_z - start_z, 0) * 4.0

        # Closer to peak center
        start_center = np.sqrt(start_x**2 + start_y**2)
        end_center = np.sqrt(end_x**2 + end_y**2)
        center_reward = (start_center - end_center) * 2.5

        # Small movement reward to encourage exploration
        movement_bonus = np.linalg.norm(np.array(self.last_position) - np.array(self.start_position)) * 0.4

        fitness = forward_reward + height_reward + center_reward + movement_bonus
        return max(fitness, 0.0)

    def update_dna(self, dna):
        self.dna = dna
        self.flat_links = None
        self.exp_links = None
        self.motors = None
        self.start_position = None
        self.last_position = None