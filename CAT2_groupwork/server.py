"""
Poultry Farm Management System — Web GUI server
--------------------------------------------------
This file is NEW and does not modify any existing project files
(backend.py, main.py, UI.py, SortingModule.py, SystemSearch.py,
HealthAlertMinHeap.py, app.js are all untouched).

It simply wraps the existing `PoultryFarmSystem` (imported from
main.py) with a small Flask REST API, and serves a static web page
(templates/index.html + static/style.css + static/app.js) that talks
to that API. This gives the team a browser-based GUI on top of the
exact same backend logic used by the CLI (UI.py).

Run with:
    pip install flask flask-cors
    python server.py

Then open:
    http://127.0.0.1:5000
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# --- Reuse the EXISTING project code, unmodified ------------------------
from backend import Bird, DuplicateTagIDError, BirdNotFoundError
from main import PoultryFarmSystem

app = Flask(__name__)
CORS(app)

# One shared in-memory system instance for the running web server.
# (Exactly the same class the CLI in main.py / UI.py already uses.)
system = PoultryFarmSystem()


def bird_to_json(bird):
    if bird is None:
        return None
    return {
        "tag_id": bird.tag_id,
        "breed": bird.breed,
        "age_weeks": bird.age_weeks,
        "weight_kg": bird.weight_kg,
        "egg_count": bird.egg_count,
        "health_status": bird.health_status,
    }


# ---------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------
# API: list / add
# ---------------------------------------------------------------------
@app.route("/api/birds", methods=["GET"])
def get_birds():
    birds = system.registry.get_all_birds()
    return jsonify([bird_to_json(b) for b in birds])


@app.route("/api/birds", methods=["POST"])
def add_bird():
    data = request.get_json(force=True) or {}
    try:
        bird = Bird(
            tag_id=str(data.get("tag_id", "")).strip(),
            breed=str(data.get("breed", "")).strip(),
            age_weeks=int(data.get("age_weeks", 0)),
            weight_kg=float(data.get("weight_kg", 0)),
            egg_count=int(data.get("egg_count", 0)),
            health_status=str(data.get("health_status") or "Healthy").strip(),
        )
        system.add_bird(bird)
        return jsonify({"success": True, "bird": bird_to_json(bird)}), 201
    except DuplicateTagIDError as e:
        return jsonify({"success": False, "error": str(e)}), 409
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ---------------------------------------------------------------------
# API: search
# Always uses the hash table (SystemSearch.py) via system.search_bird(),
# same as the CLI. That method already falls back to the registry's
# linear scan internally only if the hash table and registry ever
# drift out of sync — it is not a user-facing search option.
# ---------------------------------------------------------------------
@app.route("/api/birds/<tag_id>", methods=["GET"])
def search_bird(tag_id):
    try:
        bird = system.search_bird(tag_id)
        return jsonify({"success": True, "bird": bird_to_json(bird)})
    except BirdNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404


# ---------------------------------------------------------------------
# API: edit
# ---------------------------------------------------------------------
@app.route("/api/birds/<tag_id>", methods=["PUT", "PATCH"])
def edit_bird(tag_id):
    data = request.get_json(force=True) or {}
    updates = {}
    try:
        if "weight_kg" in data and data["weight_kg"] != "":
            updates["weight_kg"] = float(data["weight_kg"])
        if "age_weeks" in data and data["age_weeks"] != "":
            updates["age_weeks"] = int(data["age_weeks"])
        if "egg_count" in data and data["egg_count"] != "":
            updates["egg_count"] = int(data["egg_count"])
        if "health_status" in data and data["health_status"] != "":
            updates["health_status"] = str(data["health_status"]).strip()
        if "breed" in data and data["breed"] != "":
            updates["breed"] = str(data["breed"]).strip()

        updated = system.edit_bird(tag_id, **updates)
        return jsonify({"success": True, "bird": bird_to_json(updated)})
    except BirdNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except (ValueError, AttributeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ---------------------------------------------------------------------
# API: delete
# ---------------------------------------------------------------------
@app.route("/api/birds/<tag_id>", methods=["DELETE"])
def delete_bird(tag_id):
    try:
        removed = system.delete_bird(tag_id)
        return jsonify({"success": True, "bird": bird_to_json(removed)})
    except BirdNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404


# ---------------------------------------------------------------------
# API: sort
# ---------------------------------------------------------------------
@app.route("/api/sort", methods=["GET"])
def sort_birds():
    criteria = request.args.get("criteria", "weight_kg")
    sorted_birds = system.sorted_flock(criteria)
    return jsonify([bird_to_json(b) for b in sorted_birds])


# ---------------------------------------------------------------------
# API: health alerts
# ---------------------------------------------------------------------
@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    alerts = system.all_health_alerts()
    return jsonify([bird_to_json(b) for b in alerts])


@app.route("/api/alerts/most-urgent", methods=["GET"])
def most_urgent():
    bird = system.most_urgent_bird()
    return jsonify(bird_to_json(bird))


# ---------------------------------------------------------------------
# API: quick stats for the dashboard cards
# ---------------------------------------------------------------------
@app.route("/api/stats", methods=["GET"])
def stats():
    birds = system.registry.get_all_birds()
    total = len(birds)
    sick = sum(1 for b in birds if b.health_status == "Sick")
    critical = sum(1 for b in birds if b.health_status == "Critical")
    healthy = total - sick - critical
    total_eggs = sum(b.egg_count for b in birds)
    return jsonify({
        "total_birds": total,
        "healthy": healthy,
        "sick": sick,
        "critical": critical,
        "total_eggs": total_eggs,
    })


if __name__ == "__main__":
    print("=" * 60)
    print("Poultry Farm Management System — Web GUI".center(60))
    print("=" * 60)
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)
