# Fredagsbarens event-system

Flask API og Streamlit-frontend til oprettelse af events samt tilmelding og afmelding.

## Start med Docker

Docker Desktop skal køre. Kør fra projektmappen:

```bash
docker compose up --build
```

- Frontend: http://localhost:8501
- API: http://localhost:5001/events

Stop med Ctrl + C.

## Start lokalt

Installér afhængigheder med uv:

```bash
uv sync
```

Start API’en i én terminal:

```bash
uv run api.py
```

Start frontenden i en anden terminal:

```bash
uv run streamlit run app.py
```

## Data

Data gemmes i hukommelsen og nulstilles, når API’en genstartes.

## API-dokumentation

swagger.json beskriver alle seks endpoints, input og statuskoder.
Åbn filens indhold i https://editor.swagger.io/ for at se dokumentationen.