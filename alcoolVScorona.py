import pygame
import os
import random
pygame.font.init()

#inicializando a janela de jogo
ALTURA, LARGURA = 750, 750
JANELA = pygame.display.set_mode((ALTURA, LARGURA))
pygame.display.set_caption("alcoolVScorona")

#carregar as imagens
#inimigos
VIRUS = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "virus.png")), (85, 85))

#jogador
ALCOOL = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "alcool.png")), (90, 90))

#lasers
LASER_VERMELHO = pygame.image.load(os.path.join("imagens", "pixel_laser_red.png"))
LASER_VERDE = pygame.image.load(os.path.join("imagens", "pixel_laser_green.png"))
LASER_AMARELO = pygame.image.load(os.path.join("imagens", "pixel_laser_yellow.png"))
LASER_AZUL = pygame.image.load(os.path.join("imagens", "pixel_laser_blue.png"))

#fundo
FUNDO = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "fundo.png")), (ALTURA, LARGURA))
FUNDO_INICIAL = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "inicial.png")), (ALTURA, LARGURA))
FUNDO_DERROTA = pygame.transform.scale(pygame.image.load(os.path.join("imagens", "ze-gotinha.png")), (ALTURA, LARGURA))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.area = pygame.mask.from_surface(self.img)

    def draw(self, jan):
        jan.blit(self.img, (self.x, self.y))

    def mover(self, vel):
        self.y += vel

    def saida_tela(self, altura):
        return not self.y < altura and self.y >= 0

    def colisao(self, obj):
        return colide(self, obj)

class Personagem:
    RESFRIAMENTO = 30

    def __init__(self, x, y, saude=100):
        self.x = x
        self.y = y
        self.saude = saude
        self.personagem_img = None
        self.laser_img = None
        self.lasers = []
        self.contador_resfriamento = 0

    def draw(self, jan):
        jan.blit(self.personagem_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(jan)

    def mover_lasers(self, vel, obj):
        self.espera()
        for laser in self.lasers:
            laser.mover(vel)
            if laser.saida_tela(ALTURA):
                self.lasers.remove(laser)
            elif laser.colisao(obj):
                obj.saude -= 10
                self.lasers.remove(laser)

    def espera(self):
        if self.contador_resfriamento >= self.RESFRIAMENTO:
            self.contador_resfriamento = 0
        elif self.contador_resfriamento > 0:
            self.contador_resfriamento += 1

    def atirar(self):
        if self.contador_resfriamento == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.contador_resfriamento = 1

    def calcular_comprimento(self):
        return self.personagem_img.get_width()

    def calcular_largura(self):
        return self.personagem_img.get_height()

class Jogador(Personagem):
    def __init__(self, x, y, saude=100):
        super().__init__(x, y, saude)
        self.personagem_img = ALCOOL
        self.laser_img = LASER_AZUL
        self.area = pygame.mask.from_surface(self.personagem_img)
        self.vida_max = saude

    def mover_lasers(self, vel, objs):
        pontuou = False
        self.espera()
        for laser in self.lasers:
            laser.mover(vel)
            if laser.saida_tela(ALTURA):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.colisao(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        pontuou = True
        return pontuou

    def draw(self, jan):
        super().draw(jan)
        self.barra_de_vida(jan)

    def barra_de_vida(self, jan):
        pygame.draw.rect(jan, (255, 0, 0), (self.x, self.y + self.personagem_img.get_height() + 10, self.personagem_img.get_width(), 10))
        pygame.draw.rect(jan, (0, 255, 0), (self.x, self.y + self.personagem_img.get_height() + 10, self.personagem_img.get_width() * (self.saude/self.vida_max), 10))


class Inimigo(Personagem):
    MAPA_DE_CORES = {
                    "vermelho": (VIRUS, LASER_VERMELHO),
                    "verde": (VIRUS, LASER_VERDE),
                    "amarelo": (VIRUS, LASER_AMARELO)
    }

    def __init__(self, x, y, cor, saude=100):
        super().__init__(x, y, saude)
        self.personagem_img, self.laser_img = self.MAPA_DE_CORES[cor]
        self.area = pygame.mask.from_surface(self.personagem_img)

    def mover(self, vel):
        self.y += vel

    def atirar(self):
        if self.contador_resfriamento == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.contador_resfriamento = 1

def colide(obj1, obj2):
    col_x = obj2.x - obj1.x
    col_y = obj2.y - obj1.y
    return obj1.area.overlap(obj2.area, (col_x, col_y)) != None


#definir o loop em que corre o jogo
def main():
    flag = True
    FPS = 60
    nivel = 0
    vidas = 5
    pontos = 0
    fonte_principal = pygame.font.SysFont("comicsams", 50)
    fonte_derrota = pygame.font.SysFont("arialblack", 38)

    inimigos = []
    qtd_inimigos = 5
    velocidade_inimogos = 1

    velocidade_player = 5

    velocidade_laser = 5

    jogador = Jogador(300, 630)

    relogio = pygame.time.Clock()

    derrota = False
    exibicao_derrota = 0

    def recarregar_janela():
        JANELA.blit(FUNDO, (0, 0))

        # textos
        vidas_label = fonte_principal.render(f"Vidas: {vidas}", 1, (255, 255, 255))
        nivel_label = fonte_principal.render(f"Nível: {nivel}", 1, (255, 255, 255))
        score_label = fonte_principal.render(f"Score: {pontos}", 1, (255, 255, 255))

        JANELA.blit(vidas_label, (10, 10))
        JANELA.blit(nivel_label, (LARGURA - vidas_label.get_width() - 10, 10))
        JANELA.blit(score_label, (LARGURA/2 - 80, 10))

        for inimigo in inimigos:
            inimigo.draw(JANELA)

        if derrota:
            JANELA.blit(FUNDO_DERROTA, (0, 0))
            derrota_label = fonte_derrota.render("Você foi contaminado!! Vacine-se!", 1, (100, 149, 237))
            JANELA.blit(derrota_label, (LARGURA/2 - derrota_label.get_width()/2, 350))

        jogador.draw(JANELA)

        pygame.display.update()

    while flag:
        relogio.tick(FPS)
        recarregar_janela()

        if vidas <= 0 or jogador.saude <= 0:
            derrota = True
            exibicao_derrota += 1

        if derrota:
            if exibicao_derrota > FPS * 6:
                flag = False
            else:
                continue

        if len(inimigos) == 0:
            nivel += 1
            qtd_inimigos += 5
            for i in range(qtd_inimigos):
                inimigo = Inimigo(random.randrange(50, LARGURA-100), random.randrange(-1500, -100), random.choice(["amarelo", "vermelho", "verde"]))
                inimigos.append(inimigo)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                flag = False

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_ESCAPE]:
            flag = False
        if teclas[pygame.K_a] and jogador.x - velocidade_player > 0: # Tecla A move para direita
            jogador.x -= velocidade_player
        if teclas[pygame.K_d] and jogador.x + velocidade_player + jogador.calcular_comprimento() < LARGURA: # Tecla D move para esquerda
            jogador.x += velocidade_player
        if teclas[pygame.K_w] and jogador.y - velocidade_player > 0: # Tecla W move para cima
            jogador.y -= velocidade_player
        if teclas[pygame.K_s] and jogador.y + velocidade_player + jogador.calcular_largura() + 15 < ALTURA: # Tecla S move para baixo
            jogador.y += velocidade_player
        if teclas[pygame.K_RETURN]:
            jogador.atirar()

        for inimigo in inimigos[:]:
            inimigo.mover(velocidade_inimogos)
            inimigo.mover_lasers(velocidade_laser, jogador)

            if random.randrange(0, 10*FPS) == 1:
                inimigo.atirar()

            if colide(inimigo, jogador):
                jogador.saude -= 10
                inimigos.remove(inimigo)

            if inimigo.y + inimigo.calcular_comprimento() > ALTURA:
                vidas -= 1
                inimigos.remove(inimigo)


        pontuou = jogador.mover_lasers(-velocidade_laser, inimigos)
        if pontuou:
            pontos += 1

def menu():
    flag = True
    while flag:
        JANELA.blit(FUNDO_INICIAL, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                flag = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

menu()