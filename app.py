from flask import Flask, render_template, request, redirect, url_for
import json, uuid

app = Flask(__name__)
ALERTS_FILE = "alerts.json"

def load_alerts():
    try:
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET"])
def index():
    alerts = load_alerts()
    return render_template("index.html", alerts=alerts)

@app.route("/add", methods=["POST"])
def add_alert():
    alerts = load_alerts()
    alerts.append({
        "id": str(uuid.uuid4()),
        "ticker": request.form["ticker"],
        "price": float(request.form["price"]),
        "direction": request.form["direction"]
    })
    save_alerts(alerts)
    return redirect(url_for("index"))

# ★ 追加：削除
@app.route("/delete/<alert_id>", methods=["POST"])
def delete_alert(alert_id):
    alerts = load_alerts()
    alerts = [a for a in alerts if a["id"] != alert_id]
    save_alerts(alerts)
    return redirect(url_for("index"))

@app.route("/edit/<alert_id>", methods=["GET", "POST"])
def edit_alert(alert_id):
    alerts = load_alerts()
    alert = next((a for a in alerts if a["id"] == alert_id), None)

    if alert is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        alert["ticker"] = request.form["ticker"]
        alert["price"] = float(request.form["price"])
        alert["direction"] = request.form["direction"]
        save_alerts(alerts)
        return redirect(url_for("index"))

    return render_template("edit.html", alert=alert)


if __name__ == "__main__":
    app.run(debug=True)
