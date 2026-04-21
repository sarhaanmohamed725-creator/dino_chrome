import pygame
import sys
import random
import os
import math

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 950, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🦕 Dino AI PRO v2")

clock = pygame.time.Clock()
font_big   = pygame.font.SysFont("Consolas", 22, bold=True)
font_small = pygame.font.SysFont("Consolas", 16)

GROUND_Y = 230

# ══════════════════════════════════════════
#  COLORS
# ══════════════════════════════════════════
WHITE   = (255, 255, 255)
BLACK   = (10,  10,  10)
RED     = (220,  50,  50)
GREEN   = ( 50, 200,  80)
BLUE    = ( 50, 130, 255)
YELLOW  = (255, 210,  50)
GRAY    = (180, 180, 180)
DKGRAY  = ( 40,  40,  50)
ORANGE  = (255, 140,  40)
PURPLE  = (160,  60, 220)
CYAN    = ( 50, 220, 210)

# ══════════════════════════════════════════
#  LOAD ASSETS
# ══════════════════════════════════════════
def load_img(name, size):
    try:
        img = pygame.image.load(name)
        return pygame.transform.scale(img, size)
    except:
        return None

def load_snd(name):
    try:
        return pygame.mixer.Sound(name)
    except:
        return None

dino1     = load_img("dino1.png",  (44, 44))
dino2     = load_img("dino2.png",  (44, 44))
cactus_img= load_img("cactus.png", (32, 44))
bird_img  = load_img("bird.png",   (42, 30))

jump_snd  = load_snd("jump.wav")
hit_snd   = load_snd("hit.wav")
score_snd = load_snd("score.wav")

# ══════════════════════════════════════════
#  PARTICLES
# ══════════════════════════════════════════
particles = []

def spawn_particles(x, y, color, n=10):
    for _ in range(n):
        particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-5, -1),
            "life": random.randint(20, 40),
            "color": color,
            "size": random.randint(2, 5)
        })

def update_draw_particles(surface):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.2
        p["life"] -= 1
        alpha = max(0, int(255 * p["life"] / 40))
        s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["color"], alpha), (p["size"], p["size"]), p["size"])
        surface.blit(s, (int(p["x"]), int(p["y"])))
        if p["life"] <= 0:
            particles.remove(p)

# ══════════════════════════════════════════
#  STARS (night background)
# ══════════════════════════════════════════
stars = [(random.randint(0, WIDTH), random.randint(0, GROUND_Y), random.random()) for _ in range(80)]

def draw_stars(surface, alpha):
    for sx, sy, brightness in stars:
        twinkle = int(180 * brightness * (0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.003 + sx)))
        c = (twinkle, twinkle, twinkle + 40)
        r = 1 if brightness < 0.5 else 2
        pygame.draw.circle(surface, c, (sx, sy), r)

# ══════════════════════════════════════════
#  CLOUDS
# ══════════════════════════════════════════
clouds = [{"x": random.randint(0, WIDTH), "y": random.randint(30, 100), "speed": random.uniform(0.3, 0.8)} for _ in range(5)]

def draw_clouds(surface, day):
    color = (220, 220, 220) if day else (60, 60, 80)
    for c in clouds:
        pygame.draw.ellipse(surface, color, (int(c["x"]), c["y"], 80, 30))
        pygame.draw.ellipse(surface, color, (int(c["x"])+15, c["y"]-15, 50, 28))
        c["x"] -= c["speed"]
        if c["x"] < -100:
            c["x"] = WIDTH + random.randint(0, 200)
            c["y"] = random.randint(30, 100)

# ══════════════════════════════════════════
#  GROUND DETAILS
# ══════════════════════════════════════════
ground_dots = [(random.randint(0, WIDTH*3), random.randint(GROUND_Y+5, GROUND_Y+20)) for _ in range(60)]
ground_offset = 0

def draw_ground(surface, speed, day):
    global ground_offset
    ground_offset = (ground_offset + speed) % WIDTH
    gc = (200, 180, 140) if day else (70, 65, 80)
    pygame.draw.rect(surface, gc, (0, GROUND_Y+44, WIDTH, HEIGHT - GROUND_Y - 44))
    line_c = (160, 140, 100) if day else (55, 50, 65)
    pygame.draw.line(surface, line_c, (0, GROUND_Y+44), (WIDTH, GROUND_Y+44), 2)
    dot_c = (140, 120, 90) if day else (90, 85, 100)
    for gx, gy in ground_dots:
        rx = int((gx - ground_offset) % WIDTH)
        pygame.draw.circle(surface, dot_c, (rx, gy), 2)

# ══════════════════════════════════════════
#  DRAW DINO (pixel-art fallback)
# ══════════════════════════════════════════
def draw_dino_pixel(surface, rect, frame, color=(60, 180, 60)):
    x, y = rect.x, rect.y
    # body
    pygame.draw.rect(surface, color,        (x+8,  y+8,  26, 22))
    # head
    pygame.draw.rect(surface, color,        (x+18, y,    20, 18))
    # eye
    pygame.draw.rect(surface, WHITE,        (x+32, y+4,   5,  5))
    pygame.draw.rect(surface, BLACK,        (x+34, y+5,   3,  3))
    # mouth
    pygame.draw.rect(surface, (40,140,40),  (x+34, y+12,  6,  2))
    # legs
    leg = int(frame) % 2
    if leg == 0:
        pygame.draw.rect(surface, color,    (x+12, y+28,  8, 14))
        pygame.draw.rect(surface, color,    (x+22, y+30,  8, 12))
    else:
        pygame.draw.rect(surface, color,    (x+12, y+30,  8, 12))
        pygame.draw.rect(surface, color,    (x+22, y+28,  8, 14))
    # tail
    pygame.draw.rect(surface, color,        (x,    y+12, 10,  8))

def draw_cactus_pixel(surface, rect, color=(40,160,60)):
    x, y = rect.x, rect.y
    pygame.draw.rect(surface, color, (x+10, y,    12, 44))
    pygame.draw.rect(surface, color, (x,    y+10, 10, 8))
    pygame.draw.rect(surface, color, (x+22, y+16, 10, 8))
    pygame.draw.rect(surface, color, (x,    y+6,  4,  12))
    pygame.draw.rect(surface, color, (x+28, y+12, 4,  12))

def draw_bird_pixel(surface, rect, frame, color=(80,120,220)):
    x, y = rect.x, rect.y
    pygame.draw.rect(surface, color, (x+8, y+8, 26, 14))
    pygame.draw.rect(surface, color, (x+28, y+4, 12, 10))
    pygame.draw.rect(surface, WHITE, (x+36, y+5, 3, 3))
    pygame.draw.rect(surface, BLACK, (x+37, y+6, 2, 2))
    wing = int(frame*2) % 2
    if wing == 0:
        pygame.draw.rect(surface, color, (x+2, y+2, 18, 8))
    else:
        pygame.draw.rect(surface, color, (x+2, y+14, 18, 8))

# ══════════════════════════════════════════
#  STATE
# ══════════════════════════════════════════
dino      = pygame.Rect(60, GROUND_Y, 44, 44)
velocity_y = 0
gravity    = 0.75
jump_power = 15
frame      = 0
is_ducking = False

obstacles = [
    {"rect": pygame.Rect(950, 230, 32, 44),  "type": "cactus"},
    {"rect": pygame.Rect(1300, 200, 42, 30), "type": "bird", "dir": 1},
]

speed       = 6.0
score       = 0
hi_score    = 0
game_over   = False
ai_mode     = False
paused      = False
flash_timer = 0
score_flash = 0
lives       = 3
combo       = 0

# AI vars
ai_distance     = 110
ai_lr           = 3
best_score_ai   = 0
ai_confidence   = 0   # visual indicator

# High score file
HS_FILE = "highscore.txt"
if os.path.exists(HS_FILE):
    try: hi_score = int(open(HS_FILE).read())
    except: hi_score = 0

def save_score():
    global hi_score
    if score > hi_score:
        hi_score = score
        with open(HS_FILE, "w") as f:
            f.write(str(hi_score))

def reset():
    global velocity_y, score, speed, frame, game_over, particles, lives, combo, is_ducking, ai_confidence
    dino.y    = GROUND_Y
    dino.height = 44
    velocity_y = 0
    score      = 0
    speed      = 6.0
    frame      = 0
    game_over  = False
    lives      = 3
    combo      = 0
    is_ducking = False
    ai_confidence = 0
    particles.clear()
    obstacles[0]["rect"].topleft = (950, 230)
    obstacles[1]["rect"].topleft = (1300, 200)

# ══════════════════════════════════════════
#  SMART AI v2
# ══════════════════════════════════════════
def ai_think():
    global ai_confidence
    if dino.y < GROUND_Y:
        ai_confidence = 0
        return False, False   # in air – wait

    should_jump = False
    should_duck = False

    for obs in obstacles:
        dist = obs["rect"].x - dino.x
        if dist < 0 or dist > 500:
            continue

        threat = ai_distance + speed * 6

        if obs["type"] == "cactus":
            if dist < threat:
                should_jump = True
                ai_confidence = max(0, 100 - int(dist))

        elif obs["type"] == "bird":
            bird_low = obs["rect"].y > 205
            if dist < threat:
                if bird_low:
                    should_jump = True
                    ai_confidence = max(0, 100 - int(dist))
                else:
                    should_duck = True  # duck under high bird
                    ai_confidence = max(0, 100 - int(dist))

    if not should_jump and not should_duck:
        ai_confidence = max(0, ai_confidence - 2)

    return should_jump, should_duck

# ══════════════════════════════════════════
#  BUTTONS
# ══════════════════════════════════════════
btn_ai    = pygame.Rect(WIDTH-160, 10, 140, 30)
btn_pause = pygame.Rect(WIDTH-160, 46, 140, 30)

def draw_button(surface, rect, label, active=False, color=BLUE):
    c = tuple(min(255, x+40) for x in color) if active else color
    pygame.draw.rect(surface, c, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    txt = font_small.render(label, True, WHITE)
    surface.blit(txt, txt.get_rect(center=rect.center))

# ══════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════
def draw_hud(surface, day):
    tc = BLACK if day else WHITE

    # Score
    surface.blit(font_big.render(f"Score: {score}", True, tc), (10, 10))
    surface.blit(font_small.render(f"Best:  {hi_score}", True, GRAY), (10, 36))
    surface.blit(font_small.render(f"Speed: {speed:.1f}", True, ORANGE if speed > 12 else tc), (10, 54))

    # Lives
    for i in range(lives):
        pygame.draw.circle(surface, RED, (10 + i*22, 80), 8)
        pygame.draw.circle(surface, (255,100,100), (8 + i*22, 76), 3)

    # AI confidence bar
    if ai_mode:
        bar_w = 140
        pygame.draw.rect(surface, DKGRAY, (10, 95, bar_w, 12), border_radius=4)
        fill = int(bar_w * ai_confidence / 100)
        bar_color = RED if ai_confidence > 60 else YELLOW if ai_confidence > 30 else GREEN
        pygame.draw.rect(surface, bar_color, (10, 95, fill, 12), border_radius=4)
        surface.blit(font_small.render("AI radar", True, tc), (10, 110))

    # Combo
    if combo > 1:
        surf = font_big.render(f"x{combo} COMBO!", True, YELLOW)
        surface.blit(surf, surf.get_rect(center=(WIDTH//2, 20)))

    # Buttons
    draw_button(surface, btn_ai,    "🤖 AI: ON " if ai_mode else "🎮 AI: OFF", ai_mode, GREEN if ai_mode else BLUE)
    draw_button(surface, btn_pause, "⏸ PAUSE"   if not paused else "▶ RESUME",  paused, PURPLE)

def draw_game_over(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    t1 = font_big.render("💀  GAME OVER", True, RED)
    t2 = font_small.render(f"Score: {score}   Best: {hi_score}", True, WHITE)
    t3 = font_small.render("Press SPACE or any key to restart", True, GRAY)

    surface.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
    surface.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2)))
    surface.blit(t3, t3.get_rect(center=(WIDTH//2, HEIGHT//2 + 35)))

# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
while True:
    clock.tick(60)
    ticks = pygame.time.get_ticks()

    day = speed < 12

    # ── Background ──────────────────────────
    if day:
        # gradient sky
        for row in range(GROUND_Y + 44):
            t = row / (GROUND_Y + 44)
            r = int(135 + t * 80)
            g = int(180 + t * 50)
            b = int(240 - t * 30)
            pygame.draw.line(screen, (r, g, b), (0, row), (WIDTH, row))
    else:
        for row in range(GROUND_Y + 44):
            t = row / (GROUND_Y + 44)
            r = int(10 + t * 20)
            g = int(10 + t * 15)
            b = int(30 + t * 30)
            pygame.draw.line(screen, (r, g, b), (0, row), (WIDTH, row))
        draw_stars(screen, 1.0)

    draw_clouds(screen, day)
    draw_ground(screen, speed if not paused and not game_over else 0, day)

    # ── Events ──────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_score()
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_ai.collidepoint(event.pos):
                ai_mode = not ai_mode
            if btn_pause.collidepoint(event.pos):
                paused = not paused

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused

            if game_over:
                reset()
                continue

            if not ai_mode and not paused:
                if event.key in (pygame.K_SPACE, pygame.K_UP) and dino.y >= GROUND_Y:
                    velocity_y = -jump_power
                    if jump_snd: jump_snd.play()
                    spawn_particles(dino.x+22, dino.y+44, (200,200,200), 8)

                if event.key == pygame.K_DOWN:
                    is_ducking = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                is_ducking = False

    # ── AI Control ──────────────────────────
    if ai_mode and not game_over and not paused:
        do_jump, do_duck = ai_think()
        if do_jump and dino.y >= GROUND_Y:
            velocity_y = -jump_power
            if jump_snd: jump_snd.play()
            spawn_particles(dino.x+22, dino.y+44, (50,220,100), 8)
        is_ducking = do_duck

    # ── Duck logic ──────────────────────────
    if is_ducking and dino.y >= GROUND_Y:
        dino.height = 24
        dino.y = GROUND_Y + 20
    else:
        if dino.y >= GROUND_Y:
            dino.height = 44
            dino.y = GROUND_Y

    # ── Physics ─────────────────────────────
    if not game_over and not paused:
        velocity_y += gravity
        dino.y += int(velocity_y)

        if dino.y >= GROUND_Y:
            dino.y = GROUND_Y
            velocity_y = 0

        if not is_ducking:
            dino.height = 44

        # Speed up
        if speed < 20:
            speed += 0.008

        # Animation
        frame += 0.2 if not is_ducking else 0
        current_frame = frame

        # ── Obstacles ───────────────────────
        for obs in obstacles:
            obs["rect"].x -= int(speed)

            if obs["type"] == "bird":
                obs["rect"].y += obs["dir"] * 1.5
                if obs["rect"].y > 235: obs["dir"] = -1
                if obs["rect"].y < 175: obs["dir"] = 1

            if obs["rect"].x < -60:
                obs["rect"].x = random.randint(960, 1400)
                if obs["type"] == "bird":
                    obs["rect"].y = random.choice([178, 200, 222])
                else:
                    obs["rect"].y = GROUND_Y
                score += 1
                combo += 1
                if score_snd: score_snd.play()
                spawn_particles(WIDTH//2, 30, YELLOW, 12)
                score_flash = 20

            # Collision (shrunk hitbox)
            dh = dino.inflate(-10, -10)
            oh = obs["rect"].inflate(-8, -8)
            if dh.colliderect(oh):
                lives -= 1
                spawn_particles(dino.centerx, dino.centery, RED, 20)
                if hit_snd: hit_snd.play()
                if lives <= 0:
                    game_over = True
                    save_score()
                    if ai_mode:
                        if score > best_score_ai:
                            best_score_ai = score
                            ai_distance += ai_lr
                        else:
                            ai_distance -= ai_lr
                        ai_distance = max(50, min(220, ai_distance))
                else:
                    combo = 0
                    obs["rect"].x = random.randint(960, 1400)

        # Score flash
        if score_flash > 0: score_flash -= 1

    # ── Draw Dino ───────────────────────────
    if not game_over:
        drawn = False
        if is_ducking:
            color = (60,200,60) if not ai_mode else (50,180,255)
            pygame.draw.rect(screen, color, (dino.x+4, dino.y+18, 36, 20), border_radius=6)
            drawn = True
        elif int(frame) % 2 == 0 and dino1:
            screen.blit(dino1, dino)
            drawn = True
        elif dino2:
            screen.blit(dino2, dino)
            drawn = True
        if not drawn:
            draw_dino_pixel(screen, dino, frame, (50,200,80) if not ai_mode else (50,150,255))

    # ── Draw Obstacles ──────────────────────
    for obs in obstacles:
        if obs["type"] == "cactus":
            if cactus_img:
                screen.blit(cactus_img, obs["rect"])
            else:
                draw_cactus_pixel(screen, obs["rect"])
        else:
            if bird_img:
                screen.blit(bird_img, obs["rect"])
            else:
                draw_bird_pixel(screen, obs["rect"], frame)

    # ── Particles ───────────────────────────
    update_draw_particles(screen)

    # ── Score flash effect ───────────────────
    if score_flash > 0:
        sf = font_big.render(f"+1", True, YELLOW)
        alpha = int(255 * score_flash / 20)
        sf.set_alpha(alpha)
        screen.blit(sf, (WIDTH//2 - 15, 40))

    # ── HUD ─────────────────────────────────
    draw_hud(screen, day)

    # ── Pause overlay ───────────────────────
    if paused and not game_over:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0,0,0,120))
        screen.blit(ov, (0,0))
        pt = font_big.render("⏸  PAUSED", True, WHITE)
        screen.blit(pt, pt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    # ── Game Over ───────────────────────────
    if game_over:
        draw_game_over(screen)

    pygame.display.update()