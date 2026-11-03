from flask import Flask, jsonify, request

app = Flask(__name__)

# Data gemmes i hukommelsen og nulstilles ved genstart.
events = [
    {
        "id": 1,
        "title": "Quizaften",
        "date": "2026-11-13",
        "capacity": 3,
        "participants": ["Anna", "Bo"],
    },
    {
        "id": 2,
        "title": "Brætspilsaften",
        "date": "2026-11-20",
        "capacity": 5,
        "participants": [],
    },
]

next_id = 3


def find_event(event_id):
    for event in events:
        if event["id"] == event_id:
            return event
    return None


def read_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


# Hent alle events.
@app.get("/events")
def get_events():
    return jsonify(events), 200


# Hent ét event.
@app.get("/events/<int:event_id>")
def get_event(event_id):
    event = find_event(event_id)

    if event is None:
        return jsonify({"error": "Eventet findes ikke"}), 404

    return jsonify(event), 200


# Opret et event.
@app.post("/events")
def create_event():
    global next_id

    data = read_body()
    title = data.get("title")
    date = data.get("date")
    capacity = data.get("capacity")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Titel mangler"}), 400

    if not isinstance(date, str) or not date.strip():
        return jsonify({"error": "Dato mangler"}), 400

    if type(capacity) is not int or capacity <= 0:
        return jsonify({
            "error": "Antal pladser skal være et positivt heltal"
        }), 400

    event = {
        "id": next_id,
        "title": title.strip(),
        "date": date.strip(),
        "capacity": capacity,
        "participants": [],
    }

    events.append(event)
    next_id += 1

    return jsonify(event), 201


# Tilmeld en person.
@app.post("/events/<int:event_id>/signups")
def signup(event_id):
    event = find_event(event_id)

    if event is None:
        return jsonify({"error": "Eventet findes ikke"}), 404

    name = read_body().get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Navn mangler"}), 400

    name = name.strip()

    if name in event["participants"]:
        return jsonify({"error": "Du er allerede tilmeldt"}), 409

    if len(event["participants"]) >= event["capacity"]:
        return jsonify({"error": "Eventet er fuldt"}), 409

    event["participants"].append(name)

    return jsonify(event), 201


# Afmeld en person.
@app.delete("/events/<int:event_id>/signups/<name>")
def cancel_signup(event_id, name):
    event = find_event(event_id)

    if event is None:
        return jsonify({"error": "Eventet findes ikke"}), 404

    if name not in event["participants"]:
        return jsonify({"error": "Tilmeldingen findes ikke"}), 404

    event["participants"].remove(name)

    return "", 204


# Slet et event.
@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    event = find_event(event_id)

    if event is None:
        return jsonify({"error": "Eventet findes ikke"}), 404

    events.remove(event)

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)