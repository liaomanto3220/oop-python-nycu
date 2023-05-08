import pygame
import pyivp
import json
from random import choice

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
WHITE = (255, 255, 255)


class Brick():
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.valid = True
        self.poly = pyivp.string_to_poly(
            "x = " + str(x) + ", y = " + str(y) + ", format = radial, radius = " + str(radius) + ", pts = 4")
        self.get_vertex()

    def get_vertex(self):
        self.vertex = []
        self.seg = self.poly.export_seglist()
        for i in range(self.seg.size()):
            self.vertex.append((self.seg.get_vx(i), self.seg.get_vy(i)))

    def draw(self, screen):
        if self.valid:
            pygame.draw.lines(screen, WHITE, True, self.vertex)

    def dis_to_brick(self, x, y):
        return self.poly.dist_to_poly(x, y)


class Pad(Brick):
    def move(self, key):
        if key[pygame.K_LEFT] == 1 and self.x > 0:
            self.x = self.x - 4
        if key[pygame.K_RIGHT] == 1 and self.x < SCREEN_WIDTH:
            self.x = self.x + 4

        self.poly = pyivp.string_to_poly(
            "x = " + str(self.x) + ", y = " + str(self.y) + ", format = radial, radius = " + str(self.radius) + ", pts = 4")
        self.get_vertex()


class Ball():
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.x_direction = choice((-2, 2))
        self.y_direction = -2
        self.radius = radius

    def move(self):
        self.x += self.x_direction
        self.y += self.y_direction
        self.contact_detect_wall()

    def bounce(self, brick):
        if self.x < brick.x - (brick.radius / 1.414):
            self.x_direction = -2
        elif self.x > brick.x + (brick.radius / 1.414):
            self.x_direction = 2
        elif self.y < brick.y - (brick.radius / 1.414):
            self.y_direction = -2
        elif self.y > brick.y + (brick.radius / 1.414):
            self.y_direction = 2

    def contact_detect_wall(self):
        if self.x + self.radius >= SCREEN_WIDTH or\
                self.x - self.radius <= 0:
            self.x_direction = -self.x_direction

        if self.y - self.radius <= 0:
            self.y_direction = -self.y_direction

    def contact_detect_brick(self, brick):
        if (brick.dis_to_brick(self.x, self.y) - self.radius <= 0) and brick.valid:
            self.bounce(brick)
            brick.valid = False

    def contact_detect_pad(self, pad):
        if (pad.dis_to_brick(self.x, self.y) - self.radius <= 0):
            self.bounce(pad)

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius)


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Breakout')

# load config file and create objects
with open('./config/010_config.json', 'r') as f:
    config = json.load(f)

ball = Ball(config["ball_x"], config["ball_y"], config["ball_radius"])
pad = Pad(config["pad_x"], config["pad_y"], config["pad_radius"])

brick_list = []
for brick_config in config['bricks']:
    brick_list.append(
        Brick(brick_config['x'], brick_config['y'], brick_config['radius']))

# game loop
is_running = True
while is_running:
    screen.fill((0, 0, 0))
    key = pygame.key.get_pressed()
    pad.move(key)
    pad.draw(screen)
    ball.contact_detect_pad(pad)

    for brick in brick_list:
        brick.draw(screen)
        ball.contact_detect_brick(brick)
    ball.move()
    ball.draw(screen)

    # event handler
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            is_running = False
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
