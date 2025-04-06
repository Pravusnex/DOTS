# config.py
# Stores constants and configuration settings for the simulation.

import math

# --- Display Settings ---
WIDTH, HEIGHT = 1080, 1080  # Window dimensions
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
FPS = 60 # Target frames per second

# --- Colors ---
BACKGROUND_COLOR = (0, 0, 0)      # Black
CENTER_DOT_COLOR = (255, 255, 255) # White
BOUNDARY_COLOR = (255, 255, 255)   # White
STATUS_TEXT_COLOR = (255, 255, 0)  # Yellow

# --- Simulation Parameters ---
CENTER_DOT_RADIUS = 5
BOUNDARY_FACTOR = 0.9 # Boundary shapes fit within 90% of window edge
BOUNDARY_THICKNESS = 5 # Thickness of the boundary shape line
DOT_RADIUS = 5
INITIAL_DOT_SPEED = 200  # Pixels per second

# --- Timing ---
REGULAR_SPAWN_INTERVAL = 10.0 # seconds between subsequent spawns
SPLIT_DELAY = 50  # milliseconds delay after bounce before splitting (User reverted)

# --- Behavior ---
SPLIT_ANGLE_RANGE = 90 # degrees (total random angle range for split, centered towards inward normal)
INITIAL_DOT_LIMIT = 10000 # Starting dot limit

# --- Shapes ---
# Added 'Ameba' to the list
AVAILABLE_SHAPES = ['Circle', 'Square', 'Triangle', 'Parallelogram', 'Ameba']

# --- Collision Boundary Adjustment ---
# Manual offset in pixels to adjust the collision boundary relative to the
# visual boundary's inner edge. You can fine-tune these values.
# - A POSITIVE value shrinks the collision boundary further inwards.
# - A NEGATIVE value expands the collision boundary outwards.
COLLISION_BOUNDS_INWARD_OFFSET = {
    'Circle': 0.0,
    'Square': -10.0,
    'Triangle': -10.0,
    'Parallelogram': -10.0,
    'Ameba': -0.0, # Start with same offset as other polygons, adjust as needed
}