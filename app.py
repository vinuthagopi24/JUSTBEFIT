import os
import csv
import io
from datetime import datetime, date, timedelta
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, jsonify, Response, send_file
)
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "justbefit-gym-secret-key-2026")

db.init_db()


# ---------------- CONTEXT PROCESSOR ---------------- #
@app.context_processor
def inject_global_vars():
    """Injects current date, expiring alerts count and app info into all templates."""
    today = date.today()
    expiring = db.get_expiring_soon_subscriptions(days=7)
    return {
        "current_date": today.strftime("%B %d, %Y"),
        "expiring_count": len(expiring),
        "app_name": "JUSTBEFIT",
        "app_tagline": "Gym Management & Transformation Suite"
    }


# ---------------- DASHBOARD ---------------- #
@app.route("/")
def dashboard():
    metrics = db.get_dashboard_metrics()
    expiring_soon = db.get_expiring_soon_subscriptions(days=7)
    recent_attendees = db.get_today_attendance()
    plans = db.get_all_plans()
    members = db.get_all_members()
    client_analyses = db.get_all_clients_performance_analysis()
    return render_template(
        "dashboard.html",
        metrics=metrics,
        expiring_soon=expiring_soon,
        recent_attendees=recent_attendees,
        plans=plans,
        members=members,
        client_analyses=client_analyses[:4] # Top client workout reviews
    )


# ---------------- MEMBERS ---------------- #
@app.route("/members")
def members_list():
    search = request.args.get("search", "")
    status = request.args.get("status", "")
    goal = request.args.get("goal", "")
    members = db.get_all_members(search=search, status=status, goal=goal)
    plans = db.get_all_plans()
    return render_template(
        "members.html",
        members=members,
        search=search,
        status=status,
        goal=goal,
        plans=plans
    )


@app.route("/members/new", methods=["GET", "POST"])
def member_new():
    if request.method == "POST":
        data = request.form.to_dict()
        try:
            member_id = db.create_member(data)
            flash(f"Client {data.get('first_name')} registered successfully! Baseline logged.", "success")
            return redirect(url_for("member_detail", member_id=member_id))
        except Exception as e:
            flash(f"Error registering client: {str(e)}", "danger")
            return redirect(url_for("member_new"))

    plans = db.get_all_plans()
    today_str = date.today().isoformat()
    return render_template("member_form.html", plans=plans, member=None, today=today_str)


@app.route("/members/<int:member_id>")
def member_detail(member_id):
    member = db.get_member_by_id(member_id)
    if not member:
        flash("Member not found.", "warning")
        return redirect(url_for("members_list"))

    logs = db.get_member_transformation_logs(member_id)
    plans = db.get_all_plans()

    with db.get_db() as conn:
        attendance_records = conn.execute("""
            SELECT * FROM attendance
            WHERE member_id = ?
            ORDER BY log_date DESC, check_in_time DESC
            LIMIT 15
        """, (member_id,)).fetchall()
        attendance_list = [dict(r) for r in attendance_records]

    return render_template(
        "member_detail.html",
        member=member,
        logs=logs,
        plans=plans,
        attendance_list=attendance_list
    )


@app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
def member_edit(member_id):
    member = db.get_member_by_id(member_id)
    if not member:
        flash("Member not found.", "warning")
        return redirect(url_for("members_list"))

    if request.method == "POST":
        data = request.form.to_dict()
        try:
            db.update_member(member_id, data)
            flash("Client profile and workout plan updated!", "success")
            return redirect(url_for("member_detail", member_id=member_id))
        except Exception as e:
            flash(f"Error updating member: {str(e)}", "danger")

    plans = db.get_all_plans()
    return render_template("member_form.html", member=member, plans=plans)


@app.route("/members/<int:member_id>/delete", methods=["POST"])
def member_delete(member_id):
    try:
        db.delete_member(member_id)
        flash("Client removed from system.", "info")
    except Exception as e:
        flash(f"Error deleting member: {str(e)}", "danger")
    return redirect(url_for("members_list"))


# ---------------- TRANSFORMATION JOURNEY & METRICS ---------------- #
@app.route("/members/<int:member_id>/log-metric", methods=["POST"])
def log_metric(member_id):
    data = request.form.to_dict()
    data["member_id"] = member_id
    try:
        db.log_transformation_metrics(data)
        flash("New weigh-in & body measurements recorded!", "success")
    except Exception as e:
        flash(f"Error logging metric: {str(e)}", "danger")
    return redirect(url_for("member_detail", member_id=member_id))


@app.route("/members/<int:member_id>/logs/<int:log_id>/delete", methods=["POST"])
def delete_metric(member_id, log_id):
    try:
        db.delete_transformation_log(log_id)
        flash("Measurement log removed.", "info")
    except Exception as e:
        flash(f"Error deleting log: {str(e)}", "danger")
    return redirect(url_for("member_detail", member_id=member_id))


# ---------------- CLIENT WORKOUT PERFORMANCE & ANALYSIS ---------------- #
@app.route("/analysis")
def client_analysis():
    client_analyses = db.get_all_clients_performance_analysis()
    return render_template("analysis.html", clients=client_analyses)


# ---------------- SUBSCRIPTIONS ---------------- #
@app.route("/subscriptions")
def subscriptions_list():
    status_filter = request.args.get("status", "")
    subscriptions = db.get_all_subscriptions(filter_status=status_filter)
    plans = db.get_all_plans()
    members = db.get_all_members(status="active")
    expiring_soon = db.get_expiring_soon_subscriptions(days=7)
    return render_template(
        "subscriptions.html",
        subscriptions=subscriptions,
        plans=plans,
        members=members,
        status_filter=status_filter,
        expiring_count=len(expiring_soon)
    )


@app.route("/subscriptions/new", methods=["POST"])
def subscription_create():
    data = request.form.to_dict()
    try:
        db.create_subscription(data)
        flash("Subscription successfully recorded & activated!", "success")
    except Exception as e:
        flash(f"Error creating subscription: {str(e)}", "danger")

    redirect_to = request.form.get("redirect_to")
    if redirect_to:
        return redirect(redirect_to)
    return redirect(url_for("subscriptions_list"))


# ---------------- ATTENDANCE ---------------- #
@app.route("/attendance")
def attendance_view():
    today_records = db.get_today_attendance()
    members = db.get_all_members(status="active")
    currently_in = [r for r in today_records if not r.get("check_out_time")]
    return render_template(
        "attendance.html",
        today_records=today_records,
        members=members,
        currently_in=currently_in
    )


@app.route("/attendance/checkin", methods=["POST"])
def attendance_checkin():
    member_id = request.form.get("member_id")
    if not member_id:
        flash("Please select a client to check in.", "warning")
        return redirect(url_for("attendance_view"))
    
    res = db.check_in_member(int(member_id))
    if res["success"]:
        flash(res["message"], "success")
    else:
        flash(res["message"], "warning")
    return redirect(url_for("attendance_view"))


@app.route("/attendance/checkout/<int:attendance_id>", methods=["POST"])
def attendance_checkout(attendance_id):
    db.check_out_member(attendance_id)
    flash("Client checked out successfully.", "info")
    return redirect(url_for("attendance_view"))


# ---------------- PLANS ---------------- #
@app.route("/plans", methods=["GET", "POST"])
def plans_view():
    if request.method == "POST":
        data = request.form.to_dict()
        try:
            db.create_plan(data)
            flash(f"Plan '{data.get('name')}' created successfully!", "success")
        except Exception as e:
            flash(f"Error creating plan: {str(e)}", "danger")
        return redirect(url_for("plans_view"))

    plans = db.get_all_plans()
    return render_template("plans.html", plans=plans)


# ---------------- REPORTS & DATA EXPORT ---------------- #
@app.route("/reports")
def reports_view():
    metrics = db.get_dashboard_metrics()
    plans = db.get_all_plans()
    return render_template("reports.html", metrics=metrics, plans=plans)


@app.route("/export/<string:entity>")
def export_csv(entity):
    output = io.StringIO()
    writer = csv.writer(output)

    if entity == "members":
        members = db.get_all_members()
        writer.writerow(["ID", "Member Code", "First Name", "Last Name", "Email", "Phone", "Gender", "Join Date", "Target Weight (kg)", "Height (cm)", "Fitness Goal", "Workout Split", "Intensity", "Status"])
        for m in members:
            writer.writerow([
                m["id"], m["member_code"], m["first_name"], m["last_name"],
                m["email"] or "", m["phone"], m["gender"] or "", m["join_date"],
                m["target_weight"] or "", m["height_cm"] or "", m["fitness_goal"] or "",
                m["workout_split"] or "", m["workout_intensity"] or "", m["status"]
            ])
        filename = f"justbefit_members_{date.today().isoformat()}.csv"

    elif entity == "subscriptions":
        subs = db.get_all_subscriptions()
        writer.writerow(["Subscription ID", "Member Code", "Member Name", "Plan Name", "Start Date", "End Date", "Amount Paid", "Payment Method", "Status"])
        for s in subs:
            writer.writerow([
                s["id"], s["member_code"], f"{s['first_name']} {s['last_name']}",
                s["plan_name"], s["start_date"], s["end_date"], s["amount_paid"],
                s["payment_method"], s["computed_status"]
            ])
        filename = f"justbefit_subscriptions_{date.today().isoformat()}.csv"

    elif entity == "transformation":
        with db.get_db() as conn:
            logs = conn.execute("""
                SELECT tl.*, m.member_code, m.first_name, m.last_name
                FROM transformation_logs tl
                JOIN members m ON tl.member_id = m.id
                ORDER BY tl.member_id, tl.log_date
            """).fetchall()
        writer.writerow(["Log ID", "Member Code", "Member Name", "Log Date", "Weight (kg)", "Height (cm)", "BMI", "Body Fat %", "Muscle Mass %", "Chest (cm)", "Waist (cm)", "Hips (cm)", "Notes"])
        for l in logs:
            writer.writerow([
                l["id"], l["member_code"], f"{l['first_name']} {l['last_name']}",
                l["log_date"], l["weight_kg"], l["height_cm"] or "", l["bmi"] or "",
                l["body_fat_pct"] or "", l["muscle_mass_pct"] or "",
                l["chest_cm"] or "", l["waist_cm"] or "", l["hips_cm"] or "", l["notes"] or ""
            ])
        filename = f"justbefit_transformation_logs_{date.today().isoformat()}.csv"
    else:
        return "Invalid export entity", 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ---------------- JSON APIS (FOR DYNAMIC CHARTS & AJAX) ---------------- #
@app.route("/api/members/<int:member_id>/metrics")
def api_member_metrics(member_id):
    logs = db.get_member_transformation_logs(member_id)
    return jsonify({
        "labels": [l["log_date"] for l in logs],
        "weights": [l["weight_kg"] for l in logs],
        "bmis": [l["bmi"] for l in logs],
        "body_fats": [l["body_fat_pct"] for l in logs],
        "muscle_masses": [l["muscle_mass_pct"] for l in logs],
        "waists": [l["waist_cm"] for l in logs],
        "chests": [l["chest_cm"] for l in logs]
    })


@app.route("/api/stats/overview")
def api_stats():
    metrics = db.get_dashboard_metrics()
    return jsonify(metrics)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
