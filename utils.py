import pygame

BG = pygame.Color(30, 30, 30) #Black (but not too much)

TARGET_COLOR = pygame.Color(255, 255, 0)
WALL_COLOR = pygame.Color(255, 0, 0)
AGENT_COLOR = pygame.Color(15, 50, 255)

OVERLAY_OBS = pygame.Color(0, 0, 100)
OVERLAY_STIG_WALL = pygame.Color(100, 0, 0)
OVERLAY_STIG_BOUNDARY = pygame.Color(0, 0, 0)
OVERLAY_STIG_TARGET = pygame.Color(100, 100, 0)

TARGET = 1
WALL = 2
NO_MAP = 3