# Documentacion de Logica

## Reglas del puzzle
1. Dividir la grilla en rectangulos.
2. Cada rectangulo contiene un solo numero.
3. El area del rectangulo coincide con el numero.

## Solver
- Archivo: app/shikaku_solver.py
- Estrategia: backtracking con poda.

## Uso rapido
- Enviar grilla al endpoint POST /api/solve
- Recibir lista de rectangulos o error
