# ADR 0002 — Interface com o usuário

- **Status:** em aberto

## Contexto

O enunciado pede "software claro e objetivo" e que o Dijkstra receba **origem e destino** escolhidos
pelo usuário. A apresentação precisa mostrar o grafo e o resultado.

## Alternativas

| | Tkinter (como o BoscoGraph) | Web com Flask + JS | CLI + imagem (matplotlib/networkx) |
|---|---|---|---|
| Dependências | nenhuma (vem com o Python) | Flask + biblioteca JS de grafo | matplotlib |
| Você já domina? | sim | parcialmente | sim |
| Demonstração ao vivo | boa | ótima (navegador) | fraca |
| Linhas de código de interface | médio | alto (Python + HTML + JS) | baixo |
| Risco no dia da apresentação | baixo | médio (servidor, porta, navegador) | baixo |

## Perguntas antes de decidir

- P1. Quanto tempo falta até a entrega, e quanto dele você quer gastar em interface vs. algoritmo?
- P2. O professor avalia a interface ou a corretude e a explicação do algoritmo?
- P3. Qual opção deixa a separação "algoritmo puro ↔ interface" mais visível na apresentação?

## Decisão

>>> ESCREVA AQUI SUA DECISÃO (e a justificativa, respondendo P1–P3)
