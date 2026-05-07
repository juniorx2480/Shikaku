# Teoria de Algoritmos - Shikaku Solver

## Algoritmo principal
Se usa backtracking con poda para resolver puzzles Shikaku.

## Idea base
1. Tomar celdas con numero.
2. Generar rectangulos validos por celda.
3. Probar asignacion recursiva sin solapes.
4. Si hay conflicto, revertir y probar otra opcion.

## Complejidad
- Tiempo promedio: O(n*m^2)
- Peor caso: exponencial
- Espacio: O(n*m)

## Motivo de eleccion
- Garantiza encontrar solucion si existe.
- Es claro de implementar y depurar.
- Funciona bien para tamanos de grilla comunes.
