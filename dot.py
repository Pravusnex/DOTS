# dot.py
# Defines the Dot class representing particles in the simulation.

import pygame
import random
import math
# Import specific constants needed by the Dot class and its functions
from config import (DOT_RADIUS, INITIAL_DOT_SPEED, SPLIT_ANGLE_RANGE,
                    SPLIT_DELAY, CENTER_X, CENTER_Y) # Added CENTER_X/Y for fallback

# --- Helper Function ---
def random_color():
    """Returns a random bright RGB color."""
    return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

# --- Dot Class ---
class Dot:
    def __init__(self, x, y, vx, vy, color):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(vx, vy)
        self.color = color
        self.needs_split = False
        self.split_timer_start = 0
        self.last_collision_normal = None # Should point INWARDS after mark_for_split

    def move(self, dt):
        """Move the dot based on its velocity and delta time."""
        self.pos += self.vel * dt

    def draw(self, surface):
        """Draw the dot on the surface."""
        pygame.draw.circle(surface, self.color, self.pos, DOT_RADIUS)

    def mark_for_split(self, inward_collision_normal):
         """Called by Simulation upon collision to set split state."""
         if not self.needs_split:
             self.needs_split = True
             self.split_timer_start = pygame.time.get_ticks()
             # Store the INWARD normal vector (ensure it's normalized)
             if inward_collision_normal.length_squared() > 1e-9:
                 self.last_collision_normal = inward_collision_normal.normalize()
             else:
                 # Fallback if zero vector passed somehow
                 self.last_collision_normal = pygame.Vector2(0,-1) # Default pointing up (inward for bottom edge)

    def should_split(self):
        """Check if enough time has passed since reflection to split."""
        if self.needs_split:
            elapsed_time = pygame.time.get_ticks() - self.split_timer_start
            if elapsed_time >= SPLIT_DELAY: # Uses config value (currently 10ms)
                return True
        return False

    # --- UPDATED split Method with Targeted Debug Prints ---
    def split(self):
        """
        Generate two new dots based on this dot's position.
        Split angle is relative to the stored INWARD collision normal.
        """
        new_dots = []
        self.needs_split = False # Reset immediately

        # --- DEBUG: Print position when split is called ---
        parent_pos = self.pos.copy() # Make a copy in case self.pos changes unexpectedly
        #print(f"\n--- Splitting Dot ---")
        #print(f"  Parent Pos at start of split(): {parent_pos}")
        # --- End Debug ---

        if self.last_collision_normal is None:
             print("  WARNING: No collision normal stored! Using fallback direction.")
             center_fallback = pygame.Vector2(CENTER_X, CENTER_Y) # Use imported constants
             vec_to_center = center_fallback - parent_pos # Use copied parent_pos
             if vec_to_center.length_squared() > 1e-9:
                  self.last_collision_normal = vec_to_center.normalize()
             else: # If dot is exactly at center, use arbitrary direction
                  self.last_collision_normal = pygame.Vector2(0, -1)
             print(f"  Fallback Normal Used: {self.last_collision_normal}")

        # Calculate angle of the inward normal vector
        try:
            angle_from_angle_to = self.last_collision_normal.angle_to(pygame.math.Vector2(1, 0))
            # Fix potentially incorrect angle convention between angle_to and from_polar
            angle_to_use_deg = -angle_from_angle_to
        except ValueError:
             angle_to_use_deg = random.uniform(0, 360) # Random angle as last resort
             print(f"  WARNING: Normal vector was zero? Using random angle: {angle_to_use_deg:.2f}")

        stored_normal_angle = angle_to_use_deg
        # Clear stored normal after use
        self.last_collision_normal = None

        for i in range(2):
            random_offset = random.uniform(-SPLIT_ANGLE_RANGE / 2, SPLIT_ANGLE_RANGE / 2)
            split_angle_deg = stored_normal_angle + random_offset

            current_speed = INITIAL_DOT_SPEED
            new_vel = pygame.math.Vector2()
            new_vel.from_polar((current_speed, split_angle_deg)) # Uses degrees

            # Calculate offset based on new velocity
            if current_speed > 0:
                 offset_vec = new_vel.normalize() * (DOT_RADIUS * 1.1)
            else:
                 offset_vec = pygame.math.Vector2().from_polar((DOT_RADIUS * 1.1, split_angle_deg))

            # Calculate new position based on parent position + offset
            new_pos = parent_pos + offset_vec # Use copied parent_pos

            # --- DEBUG: Print calculated child position ---
            # print(f"  Child {i+1}: Target Start Pos={new_pos}, (Parent was {parent_pos}, Offset={offset_vec})")
            # --- End Debug ---

            new_dots.append(Dot(new_pos.x, new_pos.y, new_vel.x, new_vel.y, random_color()))

        # print(f"--- End Split ---") # Add simple end marker
        return new_dots
    # --- End UPDATED split Method ---