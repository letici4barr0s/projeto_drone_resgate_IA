from collections import deque
from heapq import heappush, heappop
from itertools import count
from time import perf_counter

# O mapa usa os seguintes simbolos: B = base, V = vitima, A = asfalto, L = lama,
# R = agua rasa, X = area bloqueada e * = caminho que foi escolhido pela busca.

# ============================================================
# 1. CONFIGURACAO DO PROBLEMA
# ============================================================

CUSTOS = {
    "A": 1,             # Asfalto e o terreno mais barato para o drone.
    "L": 4,             # Lama aumenta o custo do deslocamento.
    "R": 7,             # Agua rasa e ainda mais cara.
    "X": float("inf")   # Area intransponivel, o drone nao pode entrar.
}

MOVIMENTOS = [
    (-1, 0),  # Movimento para cima.
    (1, 0),   # Movimento para baixo.
    (0, -1),  # Movimento para esquerda.
    (0, 1)    # Movimento para direita.
]


# ============================================================
# 2. INSTANCIAS DE TESTE
# ============================================================

INSTANCIAS = {
    "Instancia 1 - Simples": {
        "mapa": [
            ["A", "A", "A", "A", "A"],
            ["A", "X", "L", "X", "A"],
            ["A", "A", "A", "A", "A"],
            ["X", "X", "A", "X", "X"],
            ["A", "A", "A", "A", "A"]
        ],
        "inicio": (0, 0),
        "objetivo": (4, 4)
    },

    "Instancia 2 - Custos diferentes": {
        "mapa": [
            ["X", "X", "X", "X", "X", "X", "X", "X", "X"],
            ["A", "A", "A", "A", "A", "A", "A", "A", "A"],
            ["A", "L", "L", "L", "L", "L", "L", "L", "A"],
            ["X", "X", "X", "X", "X", "X", "X", "X", "X"]
        ],
        "inicio": (2, 0),
        "objetivo": (2, 8)
    },

    "Instancia 3 - Sem solucao": {
        "mapa": [
            ["A", "A", "X", "A", "A"],
            ["A", "A", "X", "A", "A"],
            ["A", "A", "X", "A", "A"],
            ["A", "A", "X", "A", "A"],
            ["A", "A", "X", "A", "A"]
        ],
        "inicio": (0, 0),
        "objetivo": (0, 4)
    }
}


# ============================================================
# 3. FUNCOES AUXILIARES
# ============================================================

# Funcao que valida se o mapa, a base e a vitima estao dentro das regras do problema.
def validar_mapa(mapa, inicio, objetivo):
    if not mapa or not mapa[0]:
        raise ValueError("Mapa invalido: a grade nao pode estar vazia.")

    linhas = len(mapa)
    colunas = len(mapa[0])

    for linha in mapa:
        if len(linha) != colunas:
            raise ValueError("Mapa invalido: todas as linhas precisam ter o mesmo tamanho.")

    for nome, estado in [("inicio", inicio), ("objetivo", objetivo)]:
        linha, coluna = estado
        if not (0 <= linha < linhas and 0 <= coluna < colunas):
            raise ValueError(f"{nome} fora dos limites do mapa: {estado}")

        if mapa[linha][coluna] == "X":
            raise ValueError(f"{nome} nao pode estar em uma celula bloqueada: {estado}")

    return True


# Funcao que lista todas as celulas vizinhas validas que o drone pode visitar.
def obter_sucessores(mapa, estado):
    linha, coluna = estado
    sucessores = []

    for desloc_linha, desloc_coluna in MOVIMENTOS:
        nova_linha = linha + desloc_linha
        nova_coluna = coluna + desloc_coluna

        dentro_mapa = (
            0 <= nova_linha < len(mapa)
            and 0 <= nova_coluna < len(mapa[0])
        )

        if dentro_mapa:
            terreno = mapa[nova_linha][nova_coluna]

            if terreno != "X":
                sucessores.append((nova_linha, nova_coluna))

    return sucessores


# Funcao que devolve o custo de entrar na celula atual do mapa.
def calcular_custo(mapa, estado):
    linha, coluna = estado
    return CUSTOS[mapa[linha][coluna]]


# Funcao que estima a distancia restante usando a regra de Manhattan multiplicada pelo menor custo.
def calcular_manhattan(estado, objetivo, menor_custo):
    distancia = (
        abs(estado[0] - objetivo[0])
        + abs(estado[1] - objetivo[1])
    )
    return distancia * menor_custo


# Funcao que reconstrui o caminho desde o inicio ate a vitima usando os pais dos nos.
def reconstruir_caminho(pais, objetivo):
    caminho = []
    atual = objetivo

    while atual is not None:
        caminho.append(atual)
        atual = pais[atual]

    caminho.reverse()
    return caminho


# Funcao que organiza os dados finais de uma busca com caminho encontrado.
def criar_resultado(caminho, gerados, expandidos, custo, tempo):
    return {
        "caminho": caminho,
        "gerados": gerados,
        "expandidos": expandidos,
        "custo": custo,
        "passos": len(caminho) - 1 if caminho else None,
        "tempo": tempo
    }


# Funcao que padroniza a contagem de estados gerados em todos os algoritmos.
def registrar_estado_gerado(estados_gerados, estado, gerados):
    if estado not in estados_gerados:
        estados_gerados.add(estado)
        return gerados + 1, estados_gerados
    return gerados, estados_gerados


# Funcao que organiza as metricas quando nenhuma solucao e encontrada.
def criar_resultado_sem_solucao(gerados, expandidos, tempo):
    return {
        "caminho": None,
        "gerados": gerados,
        "expandidos": expandidos,
        "custo": None,
        "passos": None,
        "tempo": tempo
    }


# ============================================================
# 4. BUSCA EM LARGURA (BFS)
# ============================================================

# Funcao que explora os estados por camadas, priorizando menor numero de passos.
def busca_largura(mapa, inicio, objetivo):
    inicio_tempo = perf_counter()

    fila = deque([inicio])
    pais = {inicio: None}
    estados_gerados = {inicio}

    gerados = 1
    expandidos = 0

    while fila:
        atual = fila.popleft()

        if atual == objetivo:
            caminho = reconstruir_caminho(pais, objetivo)
            custo_total = sum(calcular_custo(mapa, estado) for estado in caminho[1:])
            return criar_resultado(
                caminho,
                gerados,
                expandidos,
                custo_total,
                perf_counter() - inicio_tempo
            )

        expandidos += 1

        for vizinho in obter_sucessores(mapa, atual):
            if vizinho not in pais:
                pais[vizinho] = atual
                fila.append(vizinho)
                gerados, estados_gerados = registrar_estado_gerado(
                    estados_gerados,
                    vizinho,
                    gerados
                )

    return criar_resultado_sem_solucao(
        gerados,
        expandidos,
        perf_counter() - inicio_tempo
    )


# ============================================================
# 5. BUSCA DE CUSTO UNIFORME (UCS)
# ============================================================

# Funcao que escolhe sempre o caminho com menor custo acumulado, mesmo que precise de mais passos.
def busca_custo_uniforme(mapa, inicio, objetivo):
    inicio_tempo = perf_counter()

    contador = count()
    fila = [(0, next(contador), inicio)]

    custos = {inicio: 0}
    pais = {inicio: None}
    estados_gerados = {inicio}

    gerados = 1
    expandidos = 0

    while fila:
        custo_atual, _, atual = heappop(fila)

        if custo_atual != custos.get(atual):
            continue

        if atual == objetivo:
            caminho = reconstruir_caminho(pais, objetivo)
            return criar_resultado(
                caminho,
                gerados,
                expandidos,
                custo_atual,
                perf_counter() - inicio_tempo
            )

        expandidos += 1

        for vizinho in obter_sucessores(mapa, atual):
            novo_custo = custo_atual + calcular_custo(mapa, vizinho)

            if novo_custo < custos.get(vizinho, float("inf")):
                custos[vizinho] = novo_custo
                pais[vizinho] = atual
                heappush(fila, (novo_custo, next(contador), vizinho))
                gerados, estados_gerados = registrar_estado_gerado(
                    estados_gerados,
                    vizinho,
                    gerados
                )

    return criar_resultado_sem_solucao(
        gerados,
        expandidos,
        perf_counter() - inicio_tempo
    )


# ============================================================
# 6. BUSCA A*
# ============================================================

# Funcao que combina custo real e estimativa para encontrar um caminho eficiente e inteligente.
def busca_a_estrela(mapa, inicio, objetivo):
    inicio_tempo = perf_counter()

    menor_custo = min(
        custo for terreno, custo in CUSTOS.items() if terreno != "X"
    )

    contador = count()
    custo_inicial = 0
    heuristica_inicial = calcular_manhattan(inicio, objetivo, menor_custo)

    fila = [
        (custo_inicial + heuristica_inicial, custo_inicial, next(contador), inicio)
    ]

    custos = {inicio: 0}
    pais = {inicio: None}
    estados_gerados = {inicio}

    gerados = 1
    expandidos = 0

    while fila:
        _, custo_atual, _, atual = heappop(fila)

        if custo_atual != custos.get(atual):
            continue

        if atual == objetivo:
            caminho = reconstruir_caminho(pais, objetivo)
            return criar_resultado(
                caminho,
                gerados,
                expandidos,
                custo_atual,
                perf_counter() - inicio_tempo
            )

        expandidos += 1

        for vizinho in obter_sucessores(mapa, atual):
            novo_custo = custo_atual + calcular_custo(mapa, vizinho)

            if novo_custo < custos.get(vizinho, float("inf")):
                custos[vizinho] = novo_custo
                pais[vizinho] = atual

                heuristica = calcular_manhattan(vizinho, objetivo, menor_custo)
                prioridade = novo_custo + heuristica

                heappush(fila, (prioridade, novo_custo, next(contador), vizinho))
                gerados, estados_gerados = registrar_estado_gerado(
                    estados_gerados,
                    vizinho,
                    gerados
                )

    return criar_resultado_sem_solucao(
        gerados,
        expandidos,
        perf_counter() - inicio_tempo
    )


# ============================================================
# 7. APRESENTACAO DOS RESULTADOS
# ============================================================

# Funcao que desenha o mapa da grade com base, vitima e caminho destacado.
def imprimir_mapa(mapa, inicio, objetivo, caminho=None):
    conjunto_caminho = set(caminho or [])

    print("Legenda: B = base, V = vitima, * = caminho, A = asfalto, L = lama, R = agua rasa, X = bloqueado")

    for linha in range(len(mapa)):
        elementos = []

        for coluna in range(len(mapa[0])):
            estado = (linha, coluna)

            if estado == inicio:
                simbolo = "B"
            elif estado == objetivo:
                simbolo = "V"
            elif estado in conjunto_caminho:
                simbolo = "*"
            else:
                simbolo = mapa[linha][coluna]

            if estado == objetivo:
                simbolo = "V"

            elementos.append(simbolo)

        print(" ".join(elementos))


# Funcao que mostra, de forma simples, o que cada algoritmo encontrou.
def imprimir_resultado(nome, resultado):
    print(f"\nAlgoritmo: {nome}")

    if resultado["caminho"] is None:
        print("Caminho encontrado: nenhum")
    else:
        print("Caminho encontrado:", resultado["caminho"])
        print("Numero de passos:", resultado["passos"])
        print("Custo total do trajeto:", resultado["custo"])

    print("Nos gerados:", resultado["gerados"])
    print("Nos expandidos:", resultado["expandidos"])
    print(f"Tempo de execucao: {resultado['tempo']:.8f} segundos")


# Funcao que executa todos os algoritmos sobre a mesma instancia e organiza os resultados.
def executar_instancia(nome, instancia):
    mapa = instancia["mapa"]
    inicio = instancia["inicio"]
    objetivo = instancia["objetivo"]

    validar_mapa(mapa, inicio, objetivo)

    print("\n" + "=" * 60)
    print(nome)
    print("=" * 60)

    print("\nMapa original:")
    imprimir_mapa(mapa, inicio, objetivo)

    algoritmos = {
        "BFS": busca_largura,
        "UCS": busca_custo_uniforme,
        "A*": busca_a_estrela
    }

    resultados = {}

    for nome_algoritmo, funcao in algoritmos.items():
        resultado = funcao(mapa, inicio, objetivo)
        resultados[nome_algoritmo] = resultado
        imprimir_resultado(nome_algoritmo, resultado)

        if resultado["caminho"] is not None:
            print("\nMapa com o caminho escolhido:")
            imprimir_mapa(mapa, inicio, objetivo, resultado["caminho"])

    return resultados


# Funcao que imprime a tabela comparativa com as metricas das buscas.
def imprimir_tabela(todos_resultados):
    print("\n" + "=" * 100)
    print("TABELA COMPARATIVA")
    print("=" * 100)

    cabecalho = (
        f"{'Instancia':30} {'Algoritmo':10} "
        f"{'Gerados':>9} {'Expandidos':>12} "
        f"{'Custo':>8} {'Passos':>8} {'Tempo (s)':>14}"
    )

    print(cabecalho)
    print("-" * 100)

    for nome_instancia, resultados in todos_resultados.items():
        for nome_algoritmo, resultado in resultados.items():
            custo = str(resultado["custo"]) if resultado["custo"] is not None else "-"
            passos = str(resultado["passos"]) if resultado["passos"] is not None else "-"

            print(
                f"{nome_instancia:30} "
                f"{nome_algoritmo:10} "
                f"{resultado['gerados']:>9} "
                f"{resultado['expandidos']:>12} "
                f"{custo:>8} "
                f"{passos:>8} "
                f"{resultado['tempo']:>14.8f}"
            )


# Funcao que verifica se a instancia atende ao requisito do professor: BFS com menos passos e custo maior.
def verificar_caso_obrigatorio(resultados):
    bfs = resultados["BFS"]
    ucs = resultados["UCS"]

    if bfs["caminho"] is None or ucs["caminho"] is None:
        return False

    return bfs["passos"] < ucs["passos"] and bfs["custo"] > ucs["custo"]


# ============================================================
# 8. EXECUCAO PRINCIPAL
# ============================================================

# Funcao principal que roda todas as instancias e imprime o resultado final para analise.
def main():
    todos_resultados = {}

    for nome, instancia in INSTANCIAS.items():
        resultados = executar_instancia(nome, instancia)
        todos_resultados[nome] = resultados

    imprimir_tabela(todos_resultados)

    print("\nVerificacao da exigencia BFS x UCS:")

    encontrou_caso = False

    for nome, resultados in todos_resultados.items():
        if verificar_caso_obrigatorio(resultados):
            print(f"Caso obrigatorio encontrado: {nome}")
            print("BFS: menos passos, mas custo maior que UCS.")
            encontrou_caso = True

    if not encontrou_caso:
        print("Nenhuma instancia demonstrou a exigencia. Revise os mapas de teste.")


if __name__ == "__main__":
    main()