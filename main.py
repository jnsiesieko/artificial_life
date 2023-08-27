import life
import pygame

if __name__ == '__main__':
    WIDTH_GAME = 900
    WIDTH_TABLO = 400
    W = WIDTH_GAME / life.FIELD_WIDTH
    FPS = 45

    WHITE = (255, 255, 255)
    GREEN = (100, 255, 100)

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH_GAME + WIDTH_TABLO, WIDTH_GAME))
    pygame.display.set_caption("LIFE")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    m = life.Map()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        m.step()

        screen.fill(WHITE)
        for item in m.field:
            pygame.draw.rect(screen, item.color if item.type == "Bot" else GREEN, (item.x * W, item.y * W, W, W))
        text_best = font.render(f'best: {m.best.points}', True, (180, 0, 0))
        text_time = font.render(f'time: {m.time}', True, (180, 0, 0))

        screen.blit(text_best, (WIDTH_GAME + 125 + 4 * W, 2 * W - 18 + 32*2))
        pygame.draw.rect(screen, m.best.color, (WIDTH_GAME + 110, 32*2, 4 * W, 4 * W))

        screen.blit(text_time, (WIDTH_GAME + 125, 10))

        pygame.display.flip()

    pygame.quit()
