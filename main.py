# MIT License
#
# Copyright (c) 2025 serhatmertsolak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygame
import random

pygame.init()

# Screen and general settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
GRAY      = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN     = (0, 255, 0)
RED       = (255, 0, 0)
BLUE      = (0, 0, 255)
YELLOW    = (255, 255, 0)
ORANGE    = (255, 165, 0)

# Game mode: "map" or "camera_view"
mode = "map"
selected_camera = None
score = 0

# Classes

class NPC:
    def __init__(self, map_width, map_height):
        # Random position within map bounds
        self.x = random.uniform(0, map_width)
        self.y = random.uniform(0, map_height)
        self.size = 10  # radius
        self.state = "normal"    # state: "normal" or "suspicious"
        self.captured = False
        self.dx = random.uniform(-1, 1) * 1.5
        self.dy = random.uniform(-1, 1) * 1.5
        self.state_timer = pygame.time.get_ticks()
    
    def update(self, map_width, map_height):
        # Move if not captured
        if not self.captured:
            self.x += self.dx
            self.y += self.dy
            # Bounce off map edges
            if self.x <= 0 or self.x >= map_width:
                self.dx = -self.dx
            if self.y <= 0 or self.y >= map_height:
                self.dy = -self.dy
            
            # Random state update every ~3 seconds
            if pygame.time.get_ticks() - self.state_timer > 3000:
                # 30% chance to become suspicious, otherwise normal
                if random.random() < 0.3:
                    self.state = "suspicious"
                else:
                    self.state = "normal"
                self.state_timer = pygame.time.get_ticks()
    
    def draw(self, surface, offset=(0, 0), scale=1.0):
        # Calculate drawn position with offset and scale
        draw_x = int((self.x - offset[0]) * scale)
        draw_y = int((self.y - offset[1]) * scale)
        if self.captured:
            color = GRAY
        else:
            # Normal: blue, Suspicious: red
            color = BLUE if self.state == "normal" else RED
        pygame.draw.circle(surface, color, (draw_x, draw_y), int(self.size * scale))
    
    def is_clicked(self, mouse_pos, offset, scale):
        # Check if mouse_pos is within NPC circle
        draw_x = int((self.x - offset[0]) * scale)
        draw_y = int((self.y - offset[1]) * scale)
        mx, my = mouse_pos
        distance = ((mx - draw_x) ** 2 + (my - draw_y) ** 2) ** 0.5
        return distance <= self.size * scale

class Camera:
    def __init__(self, icon_pos, view_rect):
        # icon_pos: position to draw camera icon on map
        # view_rect: camera view area as pygame.Rect in map coordinates
        self.icon_pos = icon_pos
        self.view_rect = view_rect
    
    def draw_icon(self, surface):
        # Draw camera icon as a simple circle
        pygame.draw.circle(surface, YELLOW, self.icon_pos, 10)
        pygame.draw.circle(surface, BLACK, self.icon_pos, 10, 2)
    
    def draw_view_overlay(self, surface):
        # Optional: outline camera view area in map mode
        pygame.draw.rect(surface, ORANGE, self.view_rect, 2)

def draw_back_button(surface, font):
    back_rect = pygame.Rect(10, 10, 80, 30)
    pygame.draw.rect(surface, GRAY, back_rect)
    pygame.draw.rect(surface, WHITE, back_rect, 2)
    text = font.render("Back", True, WHITE)
    surface.blit(text, (back_rect.x + 10, back_rect.y + 5))
    return back_rect

# Main function
def main():
    global mode, selected_camera, score

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("City Map - Security Camera Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    # Pre-generate fixed building positions
    buildings = []
    for i in range(10):
        bx = random.randint(0, SCREEN_WIDTH - 150)
        by = random.randint(0, SCREEN_HEIGHT - 150)
        bw = random.randint(50, 150)
        bh = random.randint(50, 150)
        buildings.append(pygame.Rect(bx, by, bw, bh))
    
    # Define four cameras
    cameras = [
        Camera(icon_pos=(150, 150), view_rect=pygame.Rect(100, 100, 300, 200)),
        Camera(icon_pos=(850, 150), view_rect=pygame.Rect(700, 100, 300, 200)),
        Camera(icon_pos=(150, 550), view_rect=pygame.Rect(100, 500, 300, 200)),
        Camera(icon_pos=(850, 550), view_rect=pygame.Rect(700, 500, 300, 200)),
    ]
    
    # NPCs moving randomly on the map
    num_npcs = 20
    npcs = [NPC(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(num_npcs)]
    
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if mode == "map":
                    # In map mode, click on camera icons to switch to camera view
                    for cam in cameras:
                        cam_icon_rect = pygame.Rect(cam.icon_pos[0] - 10, cam.icon_pos[1] - 10, 20, 20)
                        if cam_icon_rect.collidepoint(mouse_pos):
                            mode = "camera_view"
                            selected_camera = cam
                elif mode == "camera_view":
                    # In camera view, first check Back button
                    back_rect = pygame.Rect(10, 10, 80, 30)
                    if back_rect.collidepoint(mouse_pos):
                        mode = "map"
                        selected_camera = None
                    else:
                        # Check suspicious NPCs within camera view
                        offset = (selected_camera.view_rect.x, selected_camera.view_rect.y)
                        scale_x = SCREEN_WIDTH / selected_camera.view_rect.width
                        scale_y = SCREEN_HEIGHT / selected_camera.view_rect.height
                        scale = min(scale_x, scale_y)
                        for npc in npcs:
                            npc_rect = pygame.Rect(npc.x - npc.size, npc.y - npc.size, npc.size * 2, npc.size * 2)
                            if selected_camera.view_rect.colliderect(npc_rect):
                                if npc.is_clicked(mouse_pos, offset, scale):
                                    if npc.state == "suspicious" and not npc.captured:
                                        npc.captured = True
                                        score += 1

        # Update NPCs
        for npc in npcs:
            npc.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Drawing
        if mode == "map":
            screen.fill(DARK_GRAY)
            # Draw buildings
            for b in buildings:
                pygame.draw.rect(screen, GRAY, b)
            # Draw camera icons and optional view overlays
            for cam in cameras:
                cam.draw_icon(screen)
                # cam.draw_view_overlay(screen)  # uncomment to see view area outlines
            # Draw NPCs
            for npc in npcs:
                npc.draw(screen)

            # HUD
            hud = font.render("Map Mode - Click a camera icon to switch to view mode.", True, WHITE)
            screen.blit(hud, (10, SCREEN_HEIGHT - 30))
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH - 120, 10))

        elif mode == "camera_view" and selected_camera is not None:
            # Render the full map to a surface
            map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            map_surface.fill(DARK_GRAY)
            for b in buildings:
                pygame.draw.rect(map_surface, GRAY, b)
            for cam in cameras:
                cam.draw_icon(map_surface)
            for npc in npcs:
                npc.draw(map_surface)
            # Extract camera view area
            view_rect = selected_camera.view_rect
            cam_view_surface = map_surface.subsurface(view_rect).copy()
            cam_view_scaled = pygame.transform.scale(cam_view_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(cam_view_scaled, (0, 0))

            # Draw Back button and HUD
            back_rect = draw_back_button(screen, font)
            hud = font.render("Camera View - Click on suspicious individuals. Press Back to return to map.", True, WHITE)
            screen.blit(hud, (SCREEN_WIDTH // 2 - 300, 10))
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH - 120, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
