document.addEventListener('DOMContentLoaded', function() {
    const aiSolveBtn = document.getElementById('ai-solve');
    const receivePuzzleBtn = document.getElementById('receive-puzzle');
    const userSolveBtn = document.getElementById('user-solve');

    const aiSection = document.getElementById('ai-solve-section');
    const receiveSection = document.getElementById('receive-puzzle-section');
    const userSection = document.getElementById('user-solve-section');

    const solveForm = document.getElementById('solve-form');
    const resultDiv = document.getElementById('result');

    const matrixInput = document.getElementById('matrix-input');
    const loadMatrixButton = document.getElementById('load-matrix');
    const loadedPuzzleDiv = document.getElementById('loaded-puzzle');

    const manualControls = document.getElementById('manual-controls');
    const selectedAnchorText = document.getElementById('selected-anchor');
    const rectRowInput = document.getElementById('rect-row');
    const rectColInput = document.getElementById('rect-col');
    const rectWidthInput = document.getElementById('rect-width');
    const rectHeightInput = document.getElementById('rect-height');
    const addRectButton = document.getElementById('add-rect');
    const resetManualButton = document.getElementById('reset-manual');
    const manualMessageDiv = document.getElementById('manual-message');
    const manualRectListDiv = document.getElementById('manual-rect-list');
    const manualPuzzleDiv = document.getElementById('manual-puzzle');
    const solutionGridDiv = document.getElementById('solution-grid');

    let currentPuzzle = null;
    let manualAssignments = [];
    let selectedAnchor = null;
    let occupiedManual = new Set();
    let invalidHighlight = null;

    function hideAllSections() {
        aiSection.classList.add('hidden');
        receiveSection.classList.add('hidden');
        userSection.classList.add('hidden');
    }

    function getCellDisplay(value) {
        return value === 0 ? '' : value;
    }

    function displayGrid(grid, elementId, assignmentMap = {}) {
        const container = document.getElementById(elementId);
        container.innerHTML = '';

        const table = document.createElement('table');
        table.className = 'puzzle-grid';

        grid.forEach((row, r) => {
            const tr = document.createElement('tr');
            row.forEach((cell, c) => {
                const td = document.createElement('td');
                td.textContent = getCellDisplay(cell);
                td.dataset.row = r;
                td.dataset.col = c;
                const key = `${r},${c}`;
                const assignment = assignmentMap[key];
                td.style.borderStyle = 'solid';
                td.style.borderWidth = '1px';
                td.style.borderColor = '#000';

                if (assignment !== undefined) {
                    td.classList.add('assigned');
                    td.style.backgroundColor = assignment.color || assignment;

                    if (assignment.className) {
                        td.classList.add(assignment.className);
                    }

                    if (assignment.rectId !== undefined) {
                        const topKey = `${r - 1},${c}`;
                        const leftKey = `${r},${c - 1}`;
                        const rightKey = `${r},${c + 1}`;
                        const bottomKey = `${r + 1},${c}`;
                        const topMatch = assignmentMap[topKey] && assignmentMap[topKey].rectId === assignment.rectId;
                        const leftMatch = assignmentMap[leftKey] && assignmentMap[leftKey].rectId === assignment.rectId;
                        const rightMatch = assignmentMap[rightKey] && assignmentMap[rightKey].rectId === assignment.rectId;
                        const bottomMatch = assignmentMap[bottomKey] && assignmentMap[bottomKey].rectId === assignment.rectId;

                        td.style.borderTopWidth = topMatch ? '1px' : '5px';
                        td.style.borderLeftWidth = leftMatch ? '1px' : '5px';
                        td.style.borderRightWidth = rightMatch ? '1px' : '5px';
                        td.style.borderBottomWidth = bottomMatch ? '1px' : '5px';
                    }

                    if (assignment.borderColor) {
                        td.style.borderColor = assignment.borderColor;
                    }
                }

                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        container.appendChild(table);
    }

    function buildSolutionMap(rectangles) {
        const map = {};
        rectangles.forEach((rect, index) => {
            const color = '#c5f4c3';
            for (let r = rect.row; r < rect.row + rect.height; r += 1) {
                for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                    map[`${r},${c}`] = { rectId: index, color, borderColor: '#000' };
                }
            }
        });
        return map;
    }

    function buildManualMap() {
        const map = {};
        manualAssignments.forEach((rect, index) => {
            const color = '#c5f4c3';
            for (let r = rect.row; r < rect.row + rect.height; r += 1) {
                for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                    map[`${r},${c}`] = { rectId: index, color, borderColor: '#000' };
                }
            }
        });
        if (invalidHighlight) {
            for (let r = invalidHighlight.row; r < invalidHighlight.row + invalidHighlight.height; r += 1) {
                for (let c = invalidHighlight.col; c < invalidHighlight.col + invalidHighlight.width; c += 1) {
                    map[`${r},${c}`] = { rectId: 'invalid', color: '#f8d7da', borderColor: '#c00', className: 'incorrect-cell' };
                }
            }
        }
        return map;
    }

    function parseMatrix(text) {
        const parsed = JSON.parse(text);
        if (!Array.isArray(parsed) || parsed.length === 0) {
            throw new Error('La matriz debe ser un array bidimensional no vacío');
        }

        const normalized = [];
        let rowLength = null;

        parsed.forEach((row, rowIndex) => {
            if (!Array.isArray(row)) {
                throw new Error(`La fila ${rowIndex + 1} no es un array`);
            }
            if (rowLength === null) {
                rowLength = row.length;
            } else if (row.length !== rowLength) {
                throw new Error('Todas las filas deben tener la misma cantidad de columnas');
            }

            const normalizedRow = row.map(value => {
                if (value === null || value === undefined || value === '' || value === '0') {
                    return 0;
                }
                if (typeof value === 'string') {
                    const trimmed = value.trim();
                    if (trimmed === '' || trimmed === '0') {
                        return 0;
                    }
                    const parsedNumber = Number(trimmed);
                    if (Number.isNaN(parsedNumber)) {
                        throw new Error(`Valor inválido en la matriz: ${value}`);
                    }
                    return parsedNumber;
                }
                if (typeof value === 'number') {
                    return Math.floor(value);
                }
                throw new Error(`Valor inválido en la matriz: ${value}`);
            });

            normalized.push(normalizedRow);
        });

        return normalized;
    }

    function matrixToJson(grid) {
        return JSON.stringify(grid, null, 2);
    }

    function showManualMessage(message, isError = false) {
        manualMessageDiv.textContent = message;
        manualMessageDiv.style.color = isError ? '#b00020' : '#1f7a1f';
    }

    function updateManualAssignmentsDisplay() {
        if (!currentPuzzle) {
            manualRectListDiv.innerHTML = '';
            return;
        }

        let html = '<h3>Rectángulos agregados:</h3>';
        if (manualAssignments.length === 0) {
            html += '<p>No hay rectángulos aún.</p>';
        } else {
            html += '<ul>' + manualAssignments.map((rect, index) => {
                return `<li>Rect ${index + 1}: número ${rect.number} en (${rect.row},${rect.col}) tamaño ${rect.width}x${rect.height}</li>`;
            }).join('') + '</ul>';
        }

        manualRectListDiv.innerHTML = html;
    }

    function buildAssignmentMap() {
        const map = {};
        manualAssignments.forEach((rect, index) => {
            const color = `hsl(${(index * 60) % 360}, 70%, 80%)`;
            for (let r = rect.row; r < rect.row + rect.height; r += 1) {
                for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                    map[`${r},${c}`] = { color, borderColor: '#000' };
                }
            }
        });
        return map;
    }

    function refreshManualGrid() {
        if (!currentPuzzle) {
            document.getElementById('manual-puzzle').innerHTML = '<p>No hay puzzle cargado. Ve a "Recibir Puzzle" para cargar una matriz.</p>';
            manualControls.classList.add('hidden');
            return;
        }

        const assignmentMap = buildManualMap();
        displayGrid(currentPuzzle.grid, 'manual-puzzle', assignmentMap);
        manualControls.classList.remove('hidden');
        updateManualAssignmentsDisplay();
        selectedAnchorText.textContent = selectedAnchor ? `Celda seleccionada: (${selectedAnchor.row}, ${selectedAnchor.col}) número ${selectedAnchor.number}` : 'Celda seleccionada: ninguna';

    }

    function resetManual() {
        manualAssignments = [];
        selectedAnchor = null;
        occupiedManual = new Set();
        showManualMessage('Manual reiniciado. Selecciona una celda numerada para comenzar.');
        refreshManualGrid();
    }

    function isOverlapping(rect) {
        for (let r = rect.row; r < rect.row + rect.height; r += 1) {
            for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                if (occupiedManual.has(`${r},${c}`)) {
                    return true;
                }
            }
        }
        return false;
    }

    function markOccupied(rect) {
        for (let r = rect.row; r < rect.row + rect.height; r += 1) {
            for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                occupiedManual.add(`${r},${c}`);
            }
        }
    }

    function validateRectangle(rect) {
        if (rect.row < 0 || rect.col < 0 || rect.row + rect.height > currentPuzzle.rows || rect.col + rect.width > currentPuzzle.cols) {
            throw new Error('El rectángulo se sale de la matriz.');
        }

        if (rect.width * rect.height !== rect.number) {
            throw new Error('El área del rectángulo no coincide con el número seleccionado.');
        }

        let foundAnchor = false;
        for (let r = rect.row; r < rect.row + rect.height; r += 1) {
            for (let c = rect.col; c < rect.col + rect.width; c += 1) {
                const value = currentPuzzle.grid[r][c];
                if (value > 0) {
                    if (r === selectedAnchor.row && c === selectedAnchor.col && value === selectedAnchor.number) {
                        foundAnchor = true;
                    } else {
                        throw new Error('El rectángulo no puede contener otra celda numerada distinta.');
                    }
                }
                if (occupiedManual.has(`${r},${c}`)) {
                    throw new Error('El rectángulo se superpone con otro ya agregado.');
                }
            }
        }

        if (!foundAnchor) {
            throw new Error('El rectángulo debe cubrir la celda seleccionada.');
        }
    }

    aiSolveBtn.addEventListener('click', function() {
        hideAllSections();
        aiSection.classList.remove('hidden');
        if (currentPuzzle && !document.getElementById('grid-input').value.trim()) {
            document.getElementById('grid-input').value = matrixToJson(currentPuzzle.grid);
        }
    });

    receivePuzzleBtn.addEventListener('click', function() {
        hideAllSections();
        receiveSection.classList.remove('hidden');
    });

    userSolveBtn.addEventListener('click', function() {
        hideAllSections();
        userSection.classList.remove('hidden');
        if (currentPuzzle) {
            refreshManualGrid();
        } else {
            document.getElementById('manual-puzzle').innerHTML = '<p>No hay puzzle cargado. Ve a "Recibir Puzzle" para cargar una matriz.</p>';
            manualControls.classList.add('hidden');
        }
    });

    loadMatrixButton.addEventListener('click', function() {
        try {
            const grid = parseMatrix(matrixInput.value);
            currentPuzzle = {
                grid,
                rows: grid.length,
                cols: grid[0].length,
            };
            manualAssignments = [];
            selectedAnchor = null;
            occupiedManual = new Set();
            invalidHighlight = null;
            loadedPuzzleDiv.innerHTML = '<p>Matriz cargada correctamente.</p>';
            displayGrid(currentPuzzle.grid, 'loaded-puzzle');
            if (aiSection && !aiSection.classList.contains('hidden')) {
                document.getElementById('grid-input').value = matrixToJson(currentPuzzle.grid);
            }
        } catch (error) {
            loadedPuzzleDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            currentPuzzle = null;
        }
    });

    addRectButton.addEventListener('click', function() {
        if (!currentPuzzle) {
            showManualMessage('Carga primero una matriz en "Recibir Puzzle".', true);
            return;
        }
        if (!selectedAnchor) {
            showManualMessage('Selecciona primero una celda numerada en la cuadrícula.', true);
            return;
        }

        const row = Number(rectRowInput.value);
        const col = Number(rectColInput.value);
        const width = Number(rectWidthInput.value);
        const height = Number(rectHeightInput.value);
        if (!Number.isInteger(row) || !Number.isInteger(col) || row < 0 || col < 0) {
            showManualMessage('Ingresa fila y columna de inicio válidas.', true);
            return;
        }
        if (!width || !height) {
            showManualMessage('Ingresa ancho y alto válidos.', true);
            return;
        }

        const rect = {
            row,
            col,
            width,
            height,
            number: selectedAnchor.number,
        };

        try {
            validateRectangle(rect);
            manualAssignments.push(rect);
            markOccupied(rect);
            selectedAnchor = null;
            invalidHighlight = null;
            showManualMessage('Rectángulo agregado correctamente. Selecciona otra celda numerada.');
            refreshManualGrid();
        } catch (error) {
            invalidHighlight = rect;
            showManualMessage(error.message, true);
            refreshManualGrid();
        }
    });

    resetManualButton.addEventListener('click', function() {
        resetManual();
    });

    manualPuzzleDiv.addEventListener('click', function(event) {
        if (!currentPuzzle) return;
        const td = event.target.closest('td');
        if (!td) return;
        const row = Number(td.dataset.row);
        const col = Number(td.dataset.col);
        const value = currentPuzzle.grid[row][col];

        if (value <= 0) {
            showManualMessage('Selecciona una celda que contenga un número válido.', true);
            return;
        }

        const alreadyAssigned = manualAssignments.some(rect => {
            return row >= rect.row && row < rect.row + rect.height && col >= rect.col && col < rect.col + rect.width;
        });

        if (alreadyAssigned) {
            showManualMessage('Esta celda ya forma parte de un rectángulo.', true);
            return;
        }

        selectedAnchor = { row, col, number: value };
        selectedAnchorText.textContent = `Celda seleccionada: (${row}, ${col}) número ${value}`;
        showManualMessage('Celda seleccionada. Ingresa ancho y alto y presiona Agregar rectángulo.');
    });

    solveForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        let grid = null;
        const gridText = document.getElementById('grid-input').value.trim();
        try {
            if (gridText) {
                grid = parseMatrix(gridText);
            } else if (currentPuzzle) {
                grid = currentPuzzle.grid;
            } else {
                throw new Error('No hay matriz para resolver. Carga una en "Recibir Puzzle" o ingresa una en el formulario.');
            }

            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ grid: grid })
            });
            const data = await response.json();
            if (data.solved) {
                const solutionMap = buildSolutionMap(data.rectangles);
                resultDiv.innerHTML = `<p>Solucionado en ${data.solving_time_ms} ms</p>`;
                solutionGridDiv.innerHTML = '';
                displayGrid(grid, 'solution-grid', solutionMap);
            } else {
                resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                solutionGridDiv.innerHTML = '';
            }
        } catch (error) {
            resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    });
});