# Backend: 

Instalación rápida:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Variables de entorno (usar `.env`):


Ejecutar app de desarrollo:

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir documentación:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## Estado del proyecto

- Fase actual: backend local
- Base de datos: SQLite local (`shikaku.db`)
- Despliegue: sin Docker

## Siguiente fase (pendiente)

- Construir frontend para:
	- Crear y editar grillas Shikaku
	- Enviar puzzles al endpoint `POST /api/solve`
	- Visualizar rectángulos solución
	- Mostrar tiempos y estado de resolución

