# Level up your AI skills

Demo web creada con Codex sobre Oracle Cloud Infrastructure.

La aplicacion es un juego de preguntas de inteligencia artificial. Muestra 10 preguntas aleatorias, un temporizador de 30 segundos por pregunta y un resultado final individual con puntos, aciertos y tiempo total.

## Stack

- Oracle Cloud Infrastructure Compute
- Oracle Autonomous Transaction Processing
- Python Flask
- Gunicorn
- Nginx
- Oracle Python driver `oracledb`

## Recursos OCI usados en la demo

- Compartment: `Banco_DEMOS`
- Region de recursos: `us-chicago-1`
- VM: `linux-banco-demos-codex`
- Public IP: `147.224.177.93`
- Autonomous Database: `AIQUIZDB`
- Tabla: `AI_QUIZ_SCORES`
- URL publica: `http://147.224.177.93/`

## Variables de entorno

La aplicacion no guarda contrasenas ni llaves en el codigo. Configura estas variables en `/etc/ai-quiz.env` o en tu entorno local:

```bash
AIQUIZ_DB_USER=ADMIN
AIQUIZ_DB_PASSWORD=<password>
AIQUIZ_DB_DSN=<oracle-thin-dsn>
```

Puedes usar `.env.example` como referencia.

## Ejecutar localmente

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export AIQUIZ_DB_PASSWORD="<password>"
python app.py
```

La app local corre en `http://127.0.0.1:8000`.

## Despliegue Linux

Archivos de referencia:

- `deploy/ai-quiz.service`
- `deploy/ai-quiz-nginx.conf`

Flujo general:

```bash
sudo mkdir -p /opt/ai-quiz/templates
sudo cp app.py /opt/ai-quiz/app.py
sudo cp templates/index.html /opt/ai-quiz/templates/index.html
cd /opt/ai-quiz
python3 -m venv venv
./venv/bin/pip install -r /path/to/requirements.txt
sudo cp deploy/ai-quiz.service /etc/systemd/system/ai-quiz.service
sudo systemctl daemon-reload
sudo systemctl enable --now ai-quiz
```

Configura Nginx para hacer proxy a `127.0.0.1:8000`.

## Endpoints

- `GET /` pagina del juego
- `GET /health` valida conexion con Autonomous Database
- `GET /api/questions` entrega 10 preguntas aleatorias
- `POST /api/check` valida una respuesta
- `POST /api/submit` guarda y devuelve el resultado individual
- `GET /api/leaderboard` devuelve lista vacia para no exponer usuarios

