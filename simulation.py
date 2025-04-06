# simulation.py
# Defines the main Simulation class that orchestrates the application.

import pygame
import pygame_gui # Import the GUI library
import random
import math
import sys
from opensimplex import OpenSimplex # Use OpenSimplex

import config # Import configuration settings
from dot import Dot, random_color # Import the Dot class and helper

# --- Helper Function for Collision ---
# (find_closest_point_on_segment function remains the same)
def find_closest_point_on_segment(point_vec, seg_start_vec, seg_end_vec):
    segment_vec = seg_end_vec - seg_start_vec; seg_len_sq = segment_vec.length_squared()
    if seg_len_sq < 1e-9: return seg_start_vec
    start_to_point_vec = point_vec - seg_start_vec
    t = start_to_point_vec.dot(segment_vec) / seg_len_sq; t = max(0.0, min(1.0, t))
    closest_point = seg_start_vec + segment_vec * t
    return closest_point

# --- Main Simulation Class ---
class Simulation:
    # (__init__, define_shapes, setup_gui, reset, handle_input, spawn_dot methods remain the same as previous full script)
    def __init__(self):
        """Initializes Pygame, screen, clock, fonts, GUI, shapes, and simulation state."""
        pygame.init()
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        pygame.display.set_caption("Multi-Shape Dot Splitting Simulation")
        self.clock = pygame.time.Clock()
        try: self.font = pygame.font.SysFont(None, 30)
        except Exception as e: print(f"Warning: Font Error: {e}"); self.font = pygame.font.Font(None, 30)
        self.center_pos = pygame.math.Vector2(config.CENTER_X, config.CENTER_Y)
        self.shape_definitions = self.define_shapes()
        self.current_shape_name = config.AVAILABLE_SHAPES[0]
        if self.current_shape_name not in self.shape_definitions: self.current_shape_name = list(self.shape_definitions.keys())[0]
        self.current_shape_data = self.shape_definitions[self.current_shape_name]
        self.ui_manager = pygame_gui.UIManager((config.WIDTH, config.HEIGHT))
        self.setup_gui()
        self.reset()

    def define_shapes(self):
        """Calculates vertices and parameters for each available shape."""
        shapes = {}; max_extent_radius = int(min(config.WIDTH, config.HEIGHT) * config.BOUNDARY_FACTOR / 2)
        cx, cy = config.CENTER_X, config.CENTER_Y
        shapes['Circle'] = {'type': 'circle', 'radius': max_extent_radius}
        half_diagonal = max_extent_radius; half_side = half_diagonal / math.sqrt(2)
        shapes['Square'] = {'type': 'polygon','vertices': [(cx - half_side, cy - half_side), (cx + half_side, cy - half_side),(cx + half_side, cy + half_side), (cx - half_side, cy + half_side)]}
        v1 = self.center_pos + pygame.Vector2(0, -max_extent_radius).rotate(0); v2 = self.center_pos + pygame.Vector2(0, -max_extent_radius).rotate(120); v3 = self.center_pos + pygame.Vector2(0, -max_extent_radius).rotate(240)
        shapes['Triangle'] = {'type': 'polygon', 'vertices': [v1, v2, v3]}
        width_factor = 1.6; height_factor = 1.0; p_width = max_extent_radius * width_factor; p_height = max_extent_radius * height_factor
        angle_deg = 30; offset_x = (p_height / 2.0) / math.tan(math.radians(angle_deg)) if angle_deg % 180 != 90 else 0; half_width_base = p_width / 2.0
        v1 = (cx - half_width_base + offset_x, cy - p_height / 2.0); v2 = (cx + half_width_base + offset_x, cy - p_height / 2.0); v3 = (cx + half_width_base - offset_x, cy + p_height / 2.0); v4 = (cx - half_width_base - offset_x, cy + p_height / 2.0)
        shapes['Parallelogram'] = {'type': 'polygon', 'vertices': [v1, v2, v3, v4]}
        num_vertices_ameba = 360; ameba_vertices = []; noise_frequency = 3.0; noise_amplitude_factor = 0.4; base_r_factor = 0.55
        noise_seed = random.randint(0, 10000); print(f"Using noise seed: {noise_seed}")
        simplex = OpenSimplex(seed=noise_seed)
        generated_radii_factors = []; base_r = base_r_factor * max_extent_radius; amplitude = noise_amplitude_factor * base_r
        for i in range(num_vertices_ameba):
            theta = (i / num_vertices_ameba) * 2 * math.pi; noise_x = math.cos(theta) * noise_frequency; noise_y = math.sin(theta) * noise_frequency
            noise_val = simplex.noise2(x=noise_x, y=noise_y); current_radius = base_r + amplitude * noise_val; current_radius = max(base_r * 0.1, current_radius)
            generated_radii_factors.append(current_radius / max_extent_radius)
        max_gen_r_factor = max(generated_radii_factors) if generated_radii_factors else base_r_factor
        if max_gen_r_factor <= 1e-6: max_gen_r_factor = base_r_factor
        scale_factor = 1.0 / max_gen_r_factor
        for i in range(num_vertices_ameba):
             theta = (i / num_vertices_ameba) * 2 * math.pi; noise_x = math.cos(theta) * noise_frequency; noise_y = math.sin(theta) * noise_frequency
             noise_val = simplex.noise2(x=noise_x, y=noise_y); current_radius_unscaled = base_r + amplitude * noise_val; current_radius_unscaled = max(base_r * 0.2, current_radius_unscaled)
             r = current_radius_unscaled * scale_factor; r = min(r, max_extent_radius)
             x = cx + r * math.cos(theta); y = cy + r * math.sin(theta); ameba_vertices.append((x, y))
        shapes['Ameba'] = {'type': 'polygon', 'vertices': ameba_vertices}
        for shape_name, data in shapes.items():
            if data['type'] == 'polygon':
                 data['vertices'] = [pygame.math.Vector2(v) for v in data['vertices']]; verts = data['vertices']; data['segments'] = []
                 num_verts = len(verts)
                 for i in range(num_verts):
                      v_start = verts[i]; v_end = verts[(i + 1) % num_verts]; segment_vector = v_end - v_start; segment_len_sq = segment_vector.length_squared()
                      if segment_len_sq < 1e-9: continue
                      normal_outward = segment_vector.rotate(-90).normalize()
                      data['segments'].append((v_start, v_end, segment_vector, segment_len_sq, normal_outward))
        return shapes

    def setup_gui(self):
        dropdown_width = 150; dropdown_height = 30; padding = 10; status_text_height_approx = 30
        dropdown_rect = pygame.Rect(padding, padding + status_text_height_approx + padding, dropdown_width, dropdown_height)
        start_option = self.current_shape_name
        self.shape_dropdown = pygame_gui.elements.UIDropDownMenu(options_list=config.AVAILABLE_SHAPES, starting_option=start_option, relative_rect=dropdown_rect, manager=self.ui_manager)

    def reset(self):
        self.dots = []; self.paused = True; self.running = True; self.dot_limit = config.INITIAL_DOT_LIMIT
        self.last_spawn_time = pygame.time.get_ticks(); self.limit_reached_paused = False; self.first_unpause = True
        print("Simulation Reset and Paused."); print(f"Initial Dot Limit: {self.dot_limit}")
        if hasattr(self, 'shape_dropdown') and self.shape_dropdown: self.shape_dropdown.kill(); self.setup_gui()

    def handle_input(self, dt):
        time_delta = dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.paused:
                         if self.first_unpause:
                             if self.dot_limit > 0 and len(self.dots) == 0: self.spawn_dot()
                             self.last_spawn_time = pygame.time.get_ticks(); self.first_unpause = False
                         if self.limit_reached_paused:
                              self.dot_limit += config.INITIAL_DOT_LIMIT; self.limit_reached_paused = False; print(f"Limit Increased. New dot limit: {self.dot_limit}")
                         self.paused = False; print("Unpaused")
                    else: self.paused = True; print("Paused")
                elif event.key == pygame.K_r: self.reset()
            self.ui_manager.process_events(event)
            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == self.shape_dropdown:
                    new_shape_name = event.text
                    if new_shape_name != self.current_shape_name:
                        self.current_shape_name = new_shape_name
                        if new_shape_name in self.shape_definitions:
                             self.current_shape_data = self.shape_definitions[self.current_shape_name]; print(f"Changed shape to: {self.current_shape_name}"); self.reset()
                        else: print(f"Warning: Shape '{new_shape_name}' not found."); self.current_shape_name = config.AVAILABLE_SHAPES[0]; self.shape_dropdown.kill(); self.setup_gui()

    def spawn_dot(self):
        angle = random.uniform(0, 2 * math.pi); vel = pygame.math.Vector2(); vel.from_polar((config.INITIAL_DOT_SPEED, math.degrees(angle)))
        self.dots.append(Dot(config.CENTER_X, config.CENTER_Y, vel.x, vel.y, random_color()))

    def handle_collisions(self, dot, dt):
        shape_type = self.current_shape_data['type']; collided = False; epsilon = 1e-6
        manual_offset = config.COLLISION_BOUNDS_INWARD_OFFSET.get(self.current_shape_name, 0.0)
        if shape_type == 'circle':
            radius = self.current_shape_data['radius']; inner_boundary_edge_radius = radius - (config.BOUNDARY_THICKNESS / 2.0)
            collision_distance = max(0, inner_boundary_edge_radius - manual_offset - config.DOT_RADIUS)
            next_pos = dot.pos + dot.vel * dt; vec_to_center = self.center_pos - next_pos; dist_sq = vec_to_center.length_squared()
            if dist_sq >= (collision_distance * collision_distance) - epsilon:
                dist = math.sqrt(dist_sq) if dist_sq > 0 else 0; normal_to_center = vec_to_center.normalize() if dist > epsilon else pygame.Vector2(0, 1)
                dot.pos = self.center_pos - normal_to_center * (collision_distance - epsilon); reflection_normal = -normal_to_center
                if dot.vel.length_squared() > epsilon: dot.vel = dot.vel.reflect(reflection_normal)
                dot.mark_for_split(normal_to_center); collided = True
        elif shape_type == 'polygon':
            min_collision_dt = float('inf'); colliding_segment_data = None; final_collision_point = None
            for segment_data in self.current_shape_data['segments']: # Predictive Check
                v_start, v_end, seg_vec, seg_len_sq, seg_normal_outward = segment_data
                p_closest = find_closest_point_on_segment(dot.pos, v_start, v_end); vec_to_closest = p_closest - dot.pos
                moving_towards_segment_point = dot.vel.dot(vec_to_closest) > -epsilon; moving_towards_wall_line = dot.vel.dot(seg_normal_outward) > epsilon
                if not (moving_towards_segment_point and moving_towards_wall_line): continue
                start_to_pos = dot.pos - v_start
                dist_edge_to_target_line = start_to_pos.dot(seg_normal_outward) - (config.BOUNDARY_THICKNESS / 2.0) - manual_offset - config.DOT_RADIUS
                vel_dot_normal_positive = dot.vel.dot(seg_normal_outward)
                if abs(vel_dot_normal_positive) < epsilon: continue
                time_to_hit_line = dist_edge_to_target_line / vel_dot_normal_positive
                if 0 - epsilon <= time_to_hit_line < min_collision_dt:
                     collision_point_on_line = dot.pos + dot.vel * time_to_hit_line; vec_start_to_collision = collision_point_on_line - v_start
                     proj_on_segment_sq = vec_start_to_collision.dot(seg_vec)
                     if -epsilon <= proj_on_segment_sq <= seg_len_sq + epsilon:
                          min_collision_dt = time_to_hit_line; colliding_segment_data = segment_data; final_collision_point = collision_point_on_line
            if colliding_segment_data is not None: # Process Predictive Collision
                 v_start, v_end, seg_vec, seg_len_sq, seg_normal_outward = colliding_segment_data; dot.pos = final_collision_point
                 start_to_final_pos = dot.pos - v_start; overlap_at_collision = start_to_final_pos.dot(seg_normal_outward) - (config.BOUNDARY_THICKNESS / 2.0) - manual_offset - config.DOT_RADIUS
                 if overlap_at_collision > -epsilon: nudge_amount = overlap_at_collision + epsilon; dot.pos -= seg_normal_outward * nudge_amount
                 if dot.vel.length_squared() > epsilon: dot.vel = dot.vel.reflect(seg_normal_outward)
                 dot.mark_for_split(-seg_normal_outward); collided = True
            if not collided: # Safety Net
                next_pos = dot.pos + dot.vel * dt; max_overlap = -float('inf'); overlapping_segment_data = None
                proximity_threshold_sq = (config.DOT_RADIUS * 3)**2
                for segment_data in self.current_shape_data['segments']:
                    v_start, v_end, seg_vec, seg_len_sq, seg_normal_outward = segment_data
                    p_closest_to_next = find_closest_point_on_segment(next_pos, v_start, v_end); dist_sq_to_segment = (next_pos - p_closest_to_next).length_squared()
                    if dist_sq_to_segment > proximity_threshold_sq: continue
                    overlap = (next_pos - v_start).dot(seg_normal_outward) - (config.BOUNDARY_THICKNESS / 2.0) - manual_offset - config.DOT_RADIUS
                    if overlap > max_overlap: max_overlap = overlap; overlapping_segment_data = segment_data
                if overlapping_segment_data is not None and max_overlap > epsilon:
                    v_start, v_end, seg_vec, seg_len_sq, seg_normal_outward = overlapping_segment_data
                    moving_towards_overlap_wall = dot.vel.dot(seg_normal_outward) > epsilon
                    if moving_towards_overlap_wall:
                        dot.pos = next_pos - seg_normal_outward * (max_overlap + epsilon)
                        if dot.vel.length_squared() > epsilon: dot.vel = dot.vel.reflect(seg_normal_outward)
                        dot.mark_for_split(-seg_normal_outward); collided = True
        return collided

    def update(self, dt):
        """Updates the GUI, handles spawning, and updates dot states including collisions."""
        self.ui_manager.update(dt)
        if self.paused: return
        current_time = pygame.time.get_ticks()

        if not self.first_unpause and current_time - self.last_spawn_time >= config.REGULAR_SPAWN_INTERVAL * 1000:
            if len(self.dots) < self.dot_limit: self.spawn_dot()
            self.last_spawn_time = current_time

        dots_to_add = []; dots_to_remove = []
        for dot in self.dots:
            collision_occurred = self.handle_collisions(dot, dt)
            if not collision_occurred: dot.move(dt) # Move if no collision

            if dot.should_split():
                if len(self.dots) + len(dots_to_add) - len(dots_to_remove) < self.dot_limit:
                    # Print parent position BEFORE calling split
                    # print(f"UPDATE LOOP: Preparing to split dot at {dot.pos}")
                    new_splits = dot.split() # Call split (which now also prints position inside)
                    dots_to_add.extend(new_splits); dots_to_remove.append(dot)
                else: dot.needs_split = False

        # Apply list updates
        if dots_to_remove or dots_to_add:
             self.dots = [d for d in self.dots if d not in dots_to_remove]; self.dots.extend(dots_to_add)

        # Limit check
        if len(self.dots) >= self.dot_limit and not self.limit_reached_paused:
            self.paused = True; self.limit_reached_paused = True; print(f"Dot limit ({self.dot_limit}) reached. Paused.")


    def draw_boundary(self):
         """Draws the currently selected boundary shape."""
         shape_type = self.current_shape_data['type']; color = config.BOUNDARY_COLOR; thickness = config.BOUNDARY_THICKNESS
         if shape_type == 'circle': pygame.draw.circle(self.screen, color, self.center_pos, self.current_shape_data['radius'], thickness)
         elif shape_type == 'polygon': pygame.draw.lines(self.screen, color, True, [(v.x, v.y) for v in self.current_shape_data['vertices']], thickness)

    # --- UPDATED draw Method ---
    def draw(self):
        """Draws all simulation elements and the GUI."""
        self.screen.fill(config.BACKGROUND_COLOR)
        self.draw_boundary()
        pygame.draw.circle(self.screen, config.CENTER_DOT_COLOR, self.center_pos, config.CENTER_DOT_RADIUS)

        # --- DEBUG: Print dot positions just before drawing ---
        # print("--- Drawing Dots ---")
        # for i, dot in enumerate(self.dots):
        #     print(f"  Dot {i}: Pos={dot.pos}")
        # print("--- End Drawing Dots ---")
        # --- End Debug ---

        # Draw all simulation dots
        for dot in self.dots:
            dot.draw(self.screen) # Uses dot.pos internally

        # Draw status text (remains same)
        status_text = f"Dots: {len(self.dots)}/{self.dot_limit} | Shape: {self.current_shape_name}"
        if self.paused: status_text += " | PAUSED"
        if self.limit_reached_paused: status_text += " (Limit)"
        text_surface = self.font.render(status_text, True, config.STATUS_TEXT_COLOR)
        text_rect = text_surface.get_rect(topleft=(10, 10))
        self.screen.blit(text_surface, text_rect)

        # Draw GUI (remains same)
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()
    # --- END UPDATED draw Method ---

    def run(self):
        """Main simulation loop."""
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            if dt > 0.1: dt = 0.1 # Prevent large dt spikes
            self.handle_input(dt)
            if not self.running: break
            self.update(dt)
            self.draw()
        print("Exiting simulation.")
        if pygame.get_init(): pygame.quit()