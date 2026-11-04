# test_ga_no_threads.py
# If you on a Windows machine with any Python version 
# or an M1 mac with any Python version
# or an Intel Mac with Python > 3.7
# the multi-threaded version does not work
# so instead, you can use this version. 

import unittest
import population
import simulation 
import genome 
import creature 
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

class TestGA(unittest.TestCase):
    def testBasicGA(self):
        pop = population.Population(pop_size=20, gene_count=3)
        sim = simulation.Simulation()

        max_fits = []
        mean_fits = []
        max_links = []
        mean_links = []
        iterations = []

        os.makedirs('elite_creatures', exist_ok=True)

        try:
            for iteration in range(1000):
                for cr in pop.creatures:
                    sim.run_creature(cr, 2400)
                
                fits = [cr.new_fitness() for cr in pop.creatures]  # Use new_fitness
                links = [len(cr.get_expanded_links()) for cr in pop.creatures]
                
                print(iteration, "fittest:", np.round(np.max(fits), 3), 
                      "mean:", np.round(np.mean(fits), 3), "links mean:", np.round(np.mean(links)), "max:", np.max(links))
                
                max_fits.append(np.max(fits))
                mean_fits.append(np.mean(fits))
                max_links.append(np.max(links))
                mean_links.append(np.mean(links))
                iterations.append(iteration)
                
                fit_map = population.Population.get_fitness_map(fits)
                new_creatures = []
                for i in range(len(pop.creatures)):
                    p1_ind = population.Population.select_parent(fit_map)
                    p2_ind = population.Population.select_parent(fit_map)
                    p1 = pop.creatures[p1_ind]
                    p2 = pop.creatures[p2_ind]
                    dna = genome.Genome.crossover(p1.dna, p2.dna)
                    dna = genome.Genome.point_mutate(dna, rate=0.1, amount=0.25)
                    dna = genome.Genome.shrink_mutate(dna, rate=0.25)
                    dna = genome.Genome.grow_mutate(dna, rate=0.1)
                    cr = creature.Creature(1)
                    cr.update_dna(dna)
                    new_creatures.append(cr)
                
                max_fit = np.max(fits)
                for cr in pop.creatures:
                    if cr.new_fitness() == max_fit:
                        new_cr = creature.Creature(1)
                        new_cr.update_dna(cr.dna)
                        new_creatures[0] = new_cr
                        filename = os.path.join("elite_creatures", f"elite_{iteration}.csv")
                        genome.Genome.to_csv(cr.dna, filename)
                        break
                
                pop.creatures = new_creatures
                
        except KeyboardInterrupt:
            print("Stopped early")

        plt.figure(figsize=(10, 6))
        plt.plot(iterations, max_fits, label='Max Fitness')
        plt.plot(iterations, mean_fits, label='Mean Fitness')
        plt.xlabel('Generation')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True)
        plt.savefig('evolution_graph.png')
        plt.close()

        data = {'Iteration': iterations, 'Max Fitness': max_fits, 'Mean Fitness': mean_fits,
                'Max Links': max_links, 'Mean Links': mean_links}
        pd.DataFrame(data).to_csv('evolution_table.csv', index=False)
        print("Results saved.")

        self.assertGreater(np.max(fits), 0)

unittest.main()