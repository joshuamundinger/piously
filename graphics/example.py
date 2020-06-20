"""
Minimal pygame program to test install. Should display a red window.
"""
import pygame

dimensions = (400, 300)
background_color = (255,0,0) # red

window = pygame.display
window.set_caption('RED')

screen = window.set_mode(dimensions)
screen.fill(background_color)

# render the screen on the window
window.flip()

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
