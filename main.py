import pygame
import random
import math
import asyncio

async def main():
    pygame.init()
    WIDTH = 800
    HEIGHT = 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.Font(None,20)
    WHITE = (255, 255, 255)
    PINK = (231, 84, 128)
    PINKTWO = (255, 182, 193)
    GREEN = (193, 225, 193)
    clock = pygame.time.Clock()

    def hearts(surface, color, x, y, size):
        points = [
            (x, y +size//3)
        ]

    class Asteroid:
        def __init__(self):
            self.pos = pygame.math.Vector2(random.randint(0,WIDTH),random.randint(0,HEIGHT))
            vx = random.randint(-2,2)
            vy = random.randint(-2,2)
            if vy == 0 and vx ==0:
                vy = random.randint(-2,2)
                vx = random.randint(-2,2)

            self.vel = pygame.math.Vector2(vx, vy)
            self.color = (random.randint(0, 255), random.randint(0,255), random.randint(0,255))
            self.rad = random.randint(1, 80)
            self.mass = self.rad **2


    x = random.randint(0,800)
    y = random.randint(0,800)
    s = random.randint(0, 30)

    points = [
        (x - s, y - s),
        (x + s, y + s),
        (x, y -s // 2),
        (x - s, y-s//3),
        (x+s, y-s //3),
        (x, y + s//3)
    ]

    pygame.draw.polygon(screen,(random.randint(0, 255), random.randint(0,255), random.randint(0,255)),points )
    THRUST = 0.15
    DRAG = 0.99
    MAX_SPEED = 7
    DETECTION_RANGE = 500 
    FOV_LIM = 0.7

    ship_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
    ship_ang = 90
    ship_speed = 4
    rotation_speed = 3
    ship_rad = 20
    ship_vel = pygame.Vector2(0,0)
    ship_acc = pygame.Vector2(0,0)
    is_thrusting = False
    enemy_pos = pygame.Vector2((WIDTH/4), (HEIGHT/2))
    enemy_ang = 45


    mis_pos = ship_pos.copy()
    mis_vel = pygame.Vector2(0,0)
    mis_rad = 5
    mis_speed = 7

    asteroids = []
    for i in range(9):
        asteroids.append(Asteroid())
    running = True
    over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                tar = pygame.Vector2(event.pos)
                direction = tar - ship_pos
            
                
                if direction.length() >0:
                    direction = direction.normalize()
                    
                    mis_vel = direction * mis_speed
                    mis_pos = ship_pos.copy()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ship_ang += rotation_speed

        if keys[pygame.K_RIGHT]:
            ship_ang -= rotation_speed

        ship_acc = pygame.Vector2(0, 0)
        
        radians = math.radians(ship_ang)

        forward = pygame.Vector2(math.cos(radians), -math.sin(radians) )
        
        angle_text = font.render( f"Angle: {ship_ang:.0f}", True, WHITE)
        vector_text = font.render(f"Forward: ({forward.x:.2f}, {forward.y:.2f})", True, WHITE)
        position_text = font.render(f"Position: ({ship_pos.x:.0f}, {ship_pos.y:.2f})", True, WHITE)
        speed_text = font.render(f"Speed: {ship_vel.length():.2f}", True, WHITE)
        velocity_text = font.render(f"Velocity: ({ship_vel.x: .2f}, {ship_vel.y:.2f})", True, WHITE)

        if keys[pygame.K_UP]:
            ship_acc += forward * THRUST
            ship_vel +=ship_acc
            ship_vel *= DRAG
            
            if ship_vel.length() > MAX_SPEED:
                ship_vel.scale_to_length(MAX_SPEED)
                
            ship_pos += ship_vel
            is_thrusting = True
        if keys[pygame.K_SPACE]:
            mis_vel = forward * ship_speed 
            mis_pos = ship_pos + forward
                
        mis_pos += mis_vel
        for a in asteroids:
            a.pos += a.vel 
            
            if a.pos.x > WIDTH: 
                a.pos.x =0
                
            if a.pos.x <0:
                a.pos.x = WIDTH
                
            if a.pos.y > HEIGHT: 
                a.pos.y = 0
                
            if a.pos.y <0:
                a.pos.y = HEIGHT
        
        for i in range(len(asteroids)):
                for j in range(i+1, len(asteroids)):
                    a = asteroids[i]
                    b = asteroids[j]
                    
                    dx = a.pos.x - b.pos.x
                    dy = a.pos.y - b.pos.y
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    
                    if distance < a.rad + b.rad and distance >0:
                        normal_vector = pygame.math.Vector2(dx,dy).normalize()
                        
                        relative_vel = a.vel - b.vel
                        
                        velocity_normal = relative_vel.dot(normal_vector)
                        if velocity_normal >0:
                            continue
                        impulse = 2 * velocity_normal / (a.mass + b.mass)
                        
                        a.vel.x -= impulse * normal_vector.x
                        a.vel.y -= impulse * normal_vector.y
                        b.vel.x += impulse * normal_vector.x
                        b.vel.y += impulse * normal_vector.y
                        
                        overlap = a.rad + b.rad - distance
                        
                        a.pos.x += normal_vector.x * overlap/2
                        a.pos.y += normal_vector.y * overlap/2
                        b.pos.x -= normal_vector.x * overlap/2
                        b.pos.y -= normal_vector.y * overlap/2
        
        for a in asteroids:
            if mis_pos.distance_to(a.pos) < mis_rad + a.rad:
        
                a.pos.x = random.randint(50, 600)
                a.pos.y = random.randint(50, 600)
                mis_pos = ship_pos.copy()
                mis_vel = pygame.Vector2(0,0)
        
        nearest = min(
            asteroids, 
            key =lambda a:
            ship_pos.distance_to(a.pos)
        )
        
        radians = math.radians(enemy_ang)
        enemy_forward = pygame.Vector2((math.cos(radians)), (-math.sin(radians)))
        to_player = (ship_pos - enemy_pos)
        

        if to_player.length() >0:
            to_player = to_player.normalize() 
        
        dot = enemy_forward.dot(to_player)
        distance = enemy_pos.distance_to(ship_pos)
        
        if ( distance < DETECTION_RANGE and dot > FOV_LIM ):
            detected = True
        else:
            detected = False
            
            
        if detected: 
            enemy_color = (193, 225, 193)
            direction = ship_pos - enemy_pos
            
            if direction.length() >0:
                direction = direction.normalize()
                
                enemy_pos += direction *2 
            
        else: 
            enemy_color = (38, 153, 38)
        
        if enemy_pos.distance_to(ship_pos) < 15 + ship_rad:
            over = True
        
        
        
        
        p1 = ship_pos + forward * 22
        left = forward.rotate(140)
        right = forward.rotate(-140)

        p2 = ship_pos + left * 16
        p3 = ship_pos + right * 16



        if ship_pos.x > WIDTH:
            ship_pos.x = 0
        
        if ship_pos.x < 0:
            ship_pos.x = WIDTH
        
        if ship_pos.y > HEIGHT:
            ship_pos.y = 0
        
        if ship_pos.y < 0:
            ship_pos.y = HEIGHT
        
        screen.fill((129, 19, 49))
        screen.blit( angle_text, (10, 10) )
        screen.blit( vector_text, (10, 30) )
        screen.blit( position_text, (10, 50))
        screen.blit( speed_text, (10, 70) )
        screen.blit( velocity_text, (10, 90) )
        
        pygame.draw.polygon( screen, "white", [p1, p2, p3], 2)
        if is_thrusting: 
            back = ship_pos - forward * 18 
            back2 = ship_pos - forward * 22
            back3 = ship_pos - forward * 26
            pygame.draw.circle(screen, PINK, (int(back.x), int(back.y)), 5 )
            pygame.draw.circle(screen, PINK, (int(back2.x), int(back2.y)),  4)
            pygame.draw.circle(screen, PINK, (int(back3.x), int(back3.y)), 2)
        pygame.draw.line(
        screen,
        PINK,
        ship_pos,
        ship_pos + forward * 70,
        3
    )

        for a in asteroids:
            color = a.color
            pygame.draw.circle(screen, color , (int(a.pos.x), int(a.pos.y)), a.rad)
        
        
        pygame.draw.circle(screen,(255, 182, 193),(int(mis_pos.x), int(mis_pos.y)),mis_rad)

        pygame.draw.circle(screen, PINK, enemy_pos, DETECTION_RANGE, 1)
        pygame.draw.line(screen, PINKTWO, enemy_pos, enemy_pos + enemy_forward * 100, 3)
        pygame.draw.circle(screen, GREEN,(int(enemy_pos.x), int(enemy_pos.y)), 15)

        if over:
            over_font = pygame.font.Font(None, 60)
            over_text = over_font.render("You Died!", True, PINK)
            text_rect = over_text.get_rect (center =(WIDTH//2, HEIGHT//2 + 90))
            screen.blit(over_text, text_rect)

            pygame.display.flip()
            pygame.time.wait(4000)
            running = False
            continue

        pygame.display.flip()
        clock.tick(60)
        
        await asyncio.sleep(0)
    
asyncio.run(main())