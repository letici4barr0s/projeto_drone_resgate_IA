# Resgate em Área Alagada

Projeto desenvolvido para a disciplina de Inteligência Artificial, com o objetivo de simular o resgate de uma vítima por um drone utilizando algoritmos de busca em espaço de estados.

## Sobre o Projeto

O drone parte de uma base e deve encontrar um caminho até a vítima em um mapa representado por uma grade bidimensional. Cada célula possui um tipo de terreno, que determina o custo de deslocamento. Áreas bloqueadas não podem ser atravessadas.

O projeto implementa três algoritmos de busca: Busca em Largura (BFS), Busca de Custo Uniforme (UCS) e A*. Os resultados são comparados considerando o número de nós gerados e expandidos, o custo da solução, a quantidade de passos e o tempo de execução.

## Modelagem do Problema

### PEAS

| Componente | Descrição |
|---|---|
| Desempenho | Encontrar a vítima e minimizar o custo do percurso, evitando áreas bloqueadas. |
| Ambiente | Grade bidimensional com diferentes terrenos, obstáculos, base e vítima. |
| Atuadores | Movimentos para cima, baixo, esquerda e direita. |
| Sensores | Posição atual, mapa, custos dos terrenos e localização da base e da vítima. |

### Formulação do Problema

- **Estados:** posição do drone na grade, representada por (linha, coluna).
- **Estado inicial:** posição da base.
- **Função sucessora:** gera as posições vizinhas dentro dos limites do mapa e que não sejam bloqueadas.
- **Teste de objetivo:** verifica se o drone alcançou a posição da vítima.
- **Custo de caminho:** soma dos custos de entrada nas células percorridas.

| Terreno | Custo |
|---|---:|
| Asfalto | 1 |
| Lama | 4 |
| Água rasa | 7 |
| Área bloqueada | Intransitável |

### Classificação do Ambiente

O ambiente é completamente observável, determinístico, sequencial, estático, discreto, de agente único e conhecido. Essas características se devem ao fato de o drone conhecer o mapa e as regras, realizar movimentos previsíveis e tomar decisões que influenciam os próximos estados.

## Algoritmos Implementados

- **BFS (Busca em Largura):** explora os estados por níveis e busca o caminho com menor número de passos.
- **UCS (Busca de Custo Uniforme):** prioriza os caminhos de menor custo acumulado.
- **A* (A Estrela):** combina o custo acumulado com uma estimativa da distância restante até a vítima, utilizando a distância de Manhattan multiplicada pelo menor custo de terreno.

## Instâncias de Teste

O projeto utiliza três instâncias para avaliar o comportamento dos algoritmos:

1. **Instância 1 — Simples:** mapa pequeno para testar o funcionamento das buscas.
2. **Instância 2 — Custos diferentes:** mapa com terrenos de custos distintos para comparar o caminho de menor número de passos com o de menor custo.
3. **Instância 3 — Sem solução:** mapa com a passagem bloqueada entre a base e a vítima, utilizado para verificar se os algoritmos identificam a ausência de caminho.

## Tecnologias e Execução

O projeto foi desenvolvido em Python e utiliza as bibliotecas padrão `collections`, `heapq`, `itertools` e `time`.

Não são necessárias dependências externas.

Para executar, abra o terminal na pasta do projeto e utilize:

```bash
python3 resgate.py
```

O programa executa os três algoritmos em cada instância, apresenta os caminhos encontrados e exibe uma tabela comparativa com as métricas de desempenho.

## Divisão de Autoria

- **[Nome do integrante]:** [arquivos ou funções desenvolvidos].
- **[Nome do integrante]:** [arquivos ou funções desenvolvidos].

## Declaração de Uso de Inteligência Artificial

Foram utilizadas ferramentas de inteligência artificial como apoio ao desenvolvimento do projeto, na organização, revisão e explicação de conteúdos e/ou código.
