# main.py
# Main entry point for the simulation application.

import pygame
import sys

# Import the main Simulation class
from simulation import Simulation

if __name__ == '__main__':
    print("Starting simulation...")
    try:
        sim = Simulation()
        sim.run() # Enters the main simulation loop
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        pygame.quit() # Ensure pygame quits cleanly on error
        sys.exit(1)   # Indicate error exit status
    finally:
        # This will run even if sim.run() finishes normally or errors out
        # (unless sys.exit was called)
        if pygame.get_init(): # Check if pygame is still initialized
             pygame.quit()
    print("Simulation finished.")
    sys.exit(0) # Indicate successful exit