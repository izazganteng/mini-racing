import asyncio
import pygame

pygame.init()

screen = pygame.display.set_mode((480, 650))
pygame.display.set_caption("MINI RACING TEST")

font = pygame.font.Font(None, 50)
clock = pygame.time.Clock()

async def main():
    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 100, 40))

        text = font.render("GAME BERHASIL!", True, (255, 255, 255))
        screen.blit(text, (100, 280))

        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())
pygame.quit()
