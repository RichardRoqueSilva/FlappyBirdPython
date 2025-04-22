import pygame
import os
import random

TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # o angulo do passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2

        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_botao(tela, texto, x, y, largura, altura, cor_normal, cor_hover, fonte):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + largura and y < mouse[1] < y + altura:
        pygame.draw.rect(tela, cor_hover, (x, y, largura, altura))
    else:
        pygame.draw.rect(tela, cor_normal, (x, y, largura, altura))

    texto_render = fonte.render(texto, True, (0, 0, 0))
    tela.blit(texto_render, (x + (largura - texto_render.get_width()) // 2,
                             y + (altura - texto_render.get_height()) // 2))

    if x < mouse[0] < x + largura and y < mouse[1] < y + altura:
        if click[0] == 1:
            return True
    return False



def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()

ARQUIVO_RANKING = 'ranking.txt'

def carregar_ranking():
    if not os.path.exists(ARQUIVO_RANKING):
        return []
    with open(ARQUIVO_RANKING, 'r') as arquivo:
        linhas = arquivo.readlines()
        return sorted([int(l.strip()) for l in linhas], reverse=True)[:10]

def salvar_pontuacao(pontuacao):
    ranking = carregar_ranking()
    ranking.append(pontuacao)
    ranking = sorted(ranking, reverse=True)[:10]
    with open(ARQUIVO_RANKING, 'w') as arquivo:
        for p in ranking:
            arquivo.write(str(p) + '\n')

def tela_ranking(tela):
    fonte_titulo = pygame.font.SysFont('arial', 50)
    fonte_menor = pygame.font.SysFont('arial', 30)

    esperando = True
    while esperando:
        tela.blit(IMAGEM_BACKGROUND, (0, 0))
        titulo = fonte_titulo.render("Top 10 Pontuações", True, (255, 255, 0))
        tela.blit(titulo, (TELA_LARGURA // 2 - titulo.get_width() // 2, 60))

        ranking = carregar_ranking()
        for i, pontuacao in enumerate(ranking):
            texto = fonte_menor.render(f"{i+1}. {pontuacao} pontos", True, (255, 255, 255))
            tela.blit(texto, (TELA_LARGURA // 2 - texto.get_width() // 2, 140 + i*35))

        voltar = desenhar_botao(tela, "Voltar", TELA_LARGURA // 2 - 80, 500, 160, 50,
                                (150, 0, 0), (255, 0, 0), fonte_menor)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()

        if voltar:
            esperando = False


def tela_inicial(tela):
    fonte_titulo = pygame.font.SysFont('arial', 60)
    fonte_botao = pygame.font.SysFont('arial', 40)

    rodando = True
    while rodando:
        tela.blit(IMAGEM_BACKGROUND, (0, 0))
        titulo = fonte_titulo.render("Flappy Bird", True, (255, 255, 0))
        tela.blit(titulo, (TELA_LARGURA // 2 - titulo.get_width() // 2, 100))

        iniciar = desenhar_botao(tela, "Iniciar", TELA_LARGURA // 2 - 100, 250, 200, 60,
                                 (0, 200, 0), (0, 255, 0), fonte_botao)
        ranking = desenhar_botao(tela, "Ranking", TELA_LARGURA // 2 - 100, 330, 200, 60,
                                 (0, 0, 200), (0, 0, 255), fonte_botao)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()

        if iniciar:
            rodando = False
        if ranking:
            tela_ranking(tela)



def tela_game_over(tela, pontos):
    salvar_pontuacao(pontos)
    fonte_grande = pygame.font.SysFont('arial', 60)
    texto_game_over = fonte_grande.render("Fim de Jogo", True, (255, 0, 0))
    texto_pontuacao = FONTE_PONTOS.render(f"Pontuação: {pontos}", True, (255, 255, 255))
    texto_reiniciar = FONTE_PONTOS.render("Pressione R para reiniciar", True, (255, 255, 255))
    texto_sair = FONTE_PONTOS.render("Ou ESC para sair", True, (255, 255, 255))

    tela.blit(texto_game_over, (TELA_LARGURA // 2 - texto_game_over.get_width() // 2, 150))
    tela.blit(texto_pontuacao, (TELA_LARGURA // 2 - texto_pontuacao.get_width() // 2, 220))
    tela.blit(texto_reiniciar, (TELA_LARGURA // 2 - texto_reiniciar.get_width() // 2, 290))
    tela.blit(texto_sair, (TELA_LARGURA // 2 - texto_sair.get_width() // 2, 350))

    # Mostrar ranking
    ranking = carregar_ranking()
    fonte_menor = pygame.font.SysFont('arial', 30)
    tela.blit(fonte_menor.render("Top 10:", True, (255, 255, 0)), (30, 420))
    for i, pontuacao in enumerate(ranking):
        texto = fonte_menor.render(f"{i + 1}. {pontuacao}", True, (255, 255, 255))
        tela.blit(texto, (30, 450 + i * 25))

    pygame.display.update()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    esperando = False
                    main()
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(30)

        # interação com o usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
                # Tecla espaço
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    passaro.pular()

                # Toque na tela ou clique do mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                passaro.pular()

        # mover as coisas
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        if len(passaros) == 0:
            tela_game_over(tela, pontos)

        desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == '__main__':
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    tela_inicial(tela)
    main()


