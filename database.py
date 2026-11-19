import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "justbefit.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def calculate_bmi(weight_kg: float, height_cm: float) -> Optional[float]:
    if not weight_kg or not height_cm or height_cm <= 0:
        return None
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m * height_m), 1)


def get_bmi_category(bmi: Optional[float]) -> str:
    if bmi is None:
        return "N/A"
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal weight"
    elif bmi < 30.0:
        return "Overweight"
    elif bmi < 35.0:
        return "Obese (Class I)"
    else:
        return "Obese (Class II+)"


def init_db():
    """Initializes tables and indices."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Membership Plans Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration_months INTEGER NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                features TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Members Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_code TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                gender TEXT,
                dob DATE,
                emergency_contact TEXT,
                emergency_phone TEXT,
                join_date DATE NOT NULL,
                target_weight REAL,
                height_cm REAL,
                fitness_goal TEXT,
                workout_split TEXT,
                workout_intensity TEXT,
                nutrition_plan TEXT,
                trainer_assessment TEXT,
                medical_notes TEXT,
                avatar_url TEXT,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'frozen')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Subscriptions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                plan_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                amount_paid REAL NOT NULL,
                payment_method TEXT DEFAULT 'Cash',
                payment_status TEXT DEFAULT 'paid' CHECK(payment_status IN ('paid', 'pending', 'refunded')),
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'expired', 'expiring_soon')),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE,
                FOREIGN KEY (plan_id) REFERENCES plans (id)
            )
        """)

        # Transformation Logs Table (Weight & Body Measurements Journey)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transformation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                log_date DATE NOT NULL,
                weight_kg REAL NOT NULL,
                height_cm REAL,
                bmi REAL,
                body_fat_pct REAL,
                muscle_mass_pct REAL,
                chest_cm REAL,
                waist_cm REAL,
                hips_cm REAL,
                bicep_cm REAL,
                thigh_cm REAL,
                notes TEXT,
                photo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
            )
        """)

        # Gym Attendance Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                check_in_time TIMESTAMP NOT NULL,
                check_out_time TIMESTAMP,
                log_date DATE NOT NULL,
                FOREIGN KEY (member_id) REFERENCES members (id) ON DELETE CASCADE
            )
        """)

        # Indices for optimal query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_members_code ON members(member_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_member ON subscriptions(member_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_dates ON subscriptions(end_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trans_member ON transformation_logs(member_id, log_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_att_date ON attendance(log_date)")
        
        conn.commit()


# ---------------- MEMBER OPERATIONS ---------------- #

def generate_member_code() -> str:
    with get_db() as conn:
        row = conn.execute("SELECT id FROM members ORDER BY id DESC LIMIT 1").fetchone()
        next_id = (row["id"] + 1) if row else 1
        return f"JBF-{next_id:04d}"


def get_all_members(search: str = "", status: str = "", goal: str = "") -> List[Dict[str, Any]]:
    with get_db() as conn:
        query = """
            SELECT m.*, 
                   COALESCE(tl.weight_kg, NULL) as latest_weight,
                   COALESCE(tl.bmi, NULL) as latest_bmi,
                   s.status as sub_status,
                   s.end_date as sub_end_date,
                   p.name as plan_name
            FROM members m
            LEFT JOIN (
                SELECT member_id, weight_kg, bmi, MAX(log_date) as max_date
                FROM transformation_logs
                GROUP BY member_id
            ) tl ON m.id = tl.member_id
            LEFT JOIN (
                SELECT s1.*
                FROM subscriptions s1
                INNER JOIN (
                    SELECT member_id, MAX(end_date) as max_end
                    FROM subscriptions
                    GROUP BY member_id
                ) s2 ON s1.member_id = s2.member_id AND s1.end_date = s2.max_end
            ) s ON m.id = s.member_id
            LEFT JOIN plans p ON s.plan_id = p.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (m.first_name LIKE ? OR m.last_name LIKE ? OR m.member_code LIKE ? OR m.phone LIKE ? OR m.email LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term, term, term, term])

        if status:
            query += " AND m.status = ?"
            params.append(status)

        if goal:
            query += " AND m.fitness_goal LIKE ?"
            params.append(f"%{goal}%")

        query += " ORDER BY m.id ASC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_member_by_id(member_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if not row:
            return None
        member = dict(row)

        # Get latest transformation log
        latest_log = conn.execute(
            "SELECT * FROM transformation_logs WHERE member_id = ? ORDER BY log_date DESC, id DESC LIMIT 1",
            (member_id,)
        ).fetchone()
        member["latest_metrics"] = dict(latest_log) if latest_log else None

        # Get initial transformation log (first ever entry)
        first_log = conn.execute(
            "SELECT * FROM transformation_logs WHERE member_id = ? ORDER BY log_date ASC, id ASC LIMIT 1",
            (member_id,)
        ).fetchone()
        member["initial_metrics"] = dict(first_log) if first_log else None

        # Current Weight
        member["current_weight"] = latest_log["weight_kg"] if latest_log else None
        member["current_bmi"] = latest_log["bmi"] if latest_log else calculate_bmi(member.get("target_weight"), member.get("height_cm"))
        member["bmi_category"] = get_bmi_category(member["current_bmi"])

        # Transformation change
        if member["latest_metrics"] and member["initial_metrics"]:
            weight_diff = round(member["latest_metrics"]["weight_kg"] - member["initial_metrics"]["weight_kg"], 1)
            member["weight_change"] = weight_diff
        else:
            member["weight_change"] = 0.0

        # Active or latest subscription
        sub = conn.execute("""
            SELECT s.*, p.name as plan_name, p.duration_months
            FROM subscriptions s
            JOIN plans p ON s.plan_id = p.id
            WHERE s.member_id = ?
            ORDER BY s.end_date DESC, s.id DESC
            LIMIT 1
        """, (member_id,)).fetchone()
        member["subscription"] = dict(sub) if sub else None

        # Compute subscription days remaining
        if member["subscription"]:
            end_d = datetime.strptime(member["subscription"]["end_date"], "%Y-%m-%d").date()
            today = date.today()
            delta = (end_d - today).days
            member["subscription"]["days_remaining"] = delta
            if delta < 0:
                member["subscription"]["state"] = "expired"
            elif delta <= 7:
                member["subscription"]["state"] = "expiring_soon"
            else:
                member["subscription"]["state"] = "active"

        # Performance analysis metrics
        member["analysis"] = get_member_performance_analysis(member_id)

        return member


def create_member(data: Dict[str, Any]) -> int:
    with get_db() as conn:
        code = data.get("member_code") or generate_member_code()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (
                member_code, first_name, last_name, email, phone, gender,
                dob, emergency_contact, emergency_phone, join_date,
                target_weight, height_cm, fitness_goal, workout_split,
                workout_intensity, nutrition_plan, trainer_assessment,
                medical_notes, avatar_url, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
            data.get("first_name", "").strip(),
            data.get("last_name", "").strip() or "",
            data.get("email", "").strip() or None,
            data.get("phone", "").strip(),
            data.get("gender", "Male"),
            data.get("dob") or None,
            data.get("emergency_contact"),
            data.get("emergency_phone"),
            data.get("join_date") or date.today().isoformat(),
            float(data["target_weight"]) if data.get("target_weight") else None,
            float(data["height_cm"]) if data.get("height_cm") else None,
            data.get("fitness_goal"),
            data.get("workout_split", "Standard Strength & Cardio (4x/wk)"),
            data.get("workout_intensity", "Moderate-High"),
            data.get("nutrition_plan", "Balanced Macros & Calorie Maintenance"),
            data.get("trainer_assessment", "Newly onboarded. Focus on baseline form and technique."),
            data.get("medical_notes"),
            data.get("avatar_url") or f"https://api.dicebear.com/7.x/initials/svg?seed={data.get('first_name')}",
            data.get("status", "active")
        ))
        member_id = cursor.lastrowid

        initial_weight = data.get("initial_weight")
        if initial_weight:
            height = float(data.get("height_cm")) if data.get("height_cm") else None
            weight = float(initial_weight)
            bmi = calculate_bmi(weight, height) if height else None
            cursor.execute("""
                INSERT INTO transformation_logs (
                    member_id, log_date, weight_kg, height_cm, bmi,
                    body_fat_pct, muscle_mass_pct, chest_cm, waist_cm, hips_cm, bicep_cm, thigh_cm, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member_id,
                data.get("join_date") or date.today().isoformat(),
                weight,
                height,
                bmi,
                float(data["body_fat_pct"]) if data.get("body_fat_pct") else None,
                float(data["muscle_mass_pct"]) if data.get("muscle_mass_pct") else None,
                float(data["chest_cm"]) if data.get("chest_cm") else None,
                float(data["waist_cm"]) if data.get("waist_cm") else None,
                float(data["hips_cm"]) if data.get("hips_cm") else None,
                float(data["bicep_cm"]) if data.get("bicep_cm") else None,
                float(data["thigh_cm"]) if data.get("thigh_cm") else None,
                "Initial Registration Baseline"
            ))

        plan_id = data.get("plan_id")
        if plan_id:
            plan = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
            if plan:
                start_dt = date.today()
                duration = plan["duration_months"]
                end_dt = start_dt + timedelta(days=duration * 30)
                cursor.execute("""
                    INSERT INTO subscriptions (
                        member_id, plan_id, start_date, end_date, amount_paid,
                        payment_method, payment_status, status, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    member_id,
                    plan["id"],
                    start_dt.isoformat(),
                    end_dt.isoformat(),
                    plan["price"],
                    data.get("payment_method", "Cash"),
                    "paid",
                    "active",
                    "Initial membership subscription"
                ))

        conn.commit()
        return member_id


def update_member(member_id: int, data: Dict[str, Any]) -> bool:
    with get_db() as conn:
        conn.execute("""
            UPDATE members SET
                first_name = ?, last_name = ?, email = ?, phone = ?, gender = ?,
                dob = ?, emergency_contact = ?, emergency_phone = ?,
                target_weight = ?, height_cm = ?, fitness_goal = ?,
                workout_split = ?, workout_intensity = ?, nutrition_plan = ?,
                trainer_assessment = ?, medical_notes = ?, status = ?
            WHERE id = ?
        """, (
            data.get("first_name", "").strip(),
            data.get("last_name", "").strip() or "",
            data.get("email", "").strip() or None,
            data.get("phone", "").strip(),
            data.get("gender"),
            data.get("dob") or None,
            data.get("emergency_contact"),
            data.get("emergency_phone"),
            float(data["target_weight"]) if data.get("target_weight") else None,
            float(data["height_cm"]) if data.get("height_cm") else None,
            data.get("fitness_goal"),
            data.get("workout_split"),
            data.get("workout_intensity"),
            data.get("nutrition_plan"),
            data.get("trainer_assessment"),
            data.get("medical_notes"),
            data.get("status", "active"),
            member_id
        ))
        conn.commit()
        return True


def delete_member(member_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        return True


# ---------------- TRANSFORMATION LOGS & JOURNEY ---------------- #

def log_transformation_metrics(data: Dict[str, Any]) -> int:
    with get_db() as conn:
        weight = float(data["weight_kg"])
        member_id = int(data["member_id"])
        
        height = float(data["height_cm"]) if data.get("height_cm") else None
        if not height:
            m = conn.execute("SELECT height_cm FROM members WHERE id = ?", (member_id,)).fetchone()
            if m and m["height_cm"]:
                height = float(m["height_cm"])
                
        bmi = calculate_bmi(weight, height) if height else None
        log_d = data.get("log_date") or date.today().isoformat()

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transformation_logs (
                member_id, log_date, weight_kg, height_cm, bmi,
                body_fat_pct, muscle_mass_pct, chest_cm, waist_cm,
                hips_cm, bicep_cm, thigh_cm, notes, photo_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            member_id,
            log_d,
            weight,
            height,
            bmi,
            float(data["body_fat_pct"]) if data.get("body_fat_pct") else None,
            float(data["muscle_mass_pct"]) if data.get("muscle_mass_pct") else None,
            float(data["chest_cm"]) if data.get("chest_cm") else None,
            float(data["waist_cm"]) if data.get("waist_cm") else None,
            float(data["hips_cm"]) if data.get("hips_cm") else None,
            float(data["bicep_cm"]) if data.get("bicep_cm") else None,
            float(data["thigh_cm"]) if data.get("thigh_cm") else None,
            data.get("notes"),
            data.get("photo_url")
        ))
        conn.commit()
        return cursor.lastrowid


def get_member_transformation_logs(member_id: int) -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM transformation_logs
            WHERE member_id = ?
            ORDER BY log_date ASC, id ASC
        """, (member_id,)).fetchall()
        logs = [dict(row) for row in rows]
        for log in logs:
            log["bmi_category"] = get_bmi_category(log["bmi"])
        return logs


def delete_transformation_log(log_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM transformation_logs WHERE id = ?", (log_id,))
        conn.commit()
        return True


# ---------------- WORKOUT & PERFORMANCE ANALYSIS ---------------- #

def get_member_performance_analysis(member_id: int) -> Dict[str, Any]:
    with get_db() as conn:
        today = date.today()
        thirty_days_ago = (today - timedelta(days=30)).isoformat()

        m = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if not m:
            return {}

        total_visits = conn.execute("SELECT COUNT(*) FROM attendance WHERE member_id = ?", (member_id,)).fetchone()[0]
        recent_visits = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE member_id = ? AND log_date >= ?",
            (member_id, thirty_days_ago)
        ).fetchone()[0]

        join_dt = datetime.strptime(m["join_date"], "%Y-%m-%d").date()
        days_active = max(1, (today - join_dt).days)
        weeks_active = max(1, days_active / 7.0)
        avg_visits_week = round(total_visits / weeks_active, 1)

        target_monthly_visits = 16
        consistency_pct = min(100, int((recent_visits / target_monthly_visits) * 100))

        logs = conn.execute(
            "SELECT weight_kg, log_date FROM transformation_logs WHERE member_id = ? ORDER BY log_date ASC",
            (member_id,)
        ).fetchall()

        weight_change = 0.0
        velocity_per_month = 0.0
        goal_completion_pct = 0

        if len(logs) >= 2:
            initial_w = logs[0]["weight_kg"]
            current_w = logs[-1]["weight_kg"]
            weight_change = round(current_w - initial_w, 1)
            months = max(0.5, days_active / 30.0)
            velocity_per_month = round(weight_change / months, 1)

            target_w = m["target_weight"]
            if target_w and initial_w != target_w:
                total_to_change = abs(target_w - initial_w)
                actually_changed = abs(current_w - initial_w)
                goal_completion_pct = min(100, int((actually_changed / total_to_change) * 100))

        if consistency_pct >= 80:
            rating_badge = "Elite Dedication"
            rating_color = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
        elif consistency_pct >= 60:
            rating_badge = "Consistent"
            rating_color = "text-sky-400 bg-sky-500/10 border-sky-500/30"
        elif consistency_pct >= 40:
            rating_badge = "Steady Progress"
            rating_color = "text-amber-400 bg-amber-500/10 border-amber-500/30"
        else:
            rating_badge = "Needs Boost"
            rating_color = "text-rose-400 bg-rose-500/10 border-rose-500/30"

        return {
            "total_visits": total_visits,
            "recent_visits": recent_visits,
            "avg_visits_week": avg_visits_week,
            "consistency_pct": consistency_pct,
            "days_active": days_active,
            "weight_change": weight_change,
            "velocity_per_month": velocity_per_month,
            "goal_completion_pct": goal_completion_pct,
            "rating_badge": rating_badge,
            "rating_color": rating_color,
            "workout_split": m["workout_split"] or "Standard Strength & Conditioning",
            "workout_intensity": m["workout_intensity"] or "Moderate",
            "nutrition_plan": m["nutrition_plan"] or "Caloric Balance & Protein Target",
            "trainer_assessment": m["trainer_assessment"] or "Maintaining consistent gym floor discipline."
        }


def get_all_clients_performance_analysis() -> List[Dict[str, Any]]:
    members = get_all_members()
    analysis_list = []
    for m in members:
        detail = get_member_by_id(m["id"])
        if detail:
            analysis_list.append(detail)
    return analysis_list


# ---------------- PLANS & SUBSCRIPTIONS ---------------- #

def get_all_plans() -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM plans WHERE is_active = 1 ORDER BY duration_months ASC").fetchall()
        return [dict(r) for r in rows]


def get_plan_by_id(plan_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        return dict(row) if row else None


def create_plan(data: Dict[str, Any]) -> int:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO plans (name, duration_months, price, description, features)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["name"],
            int(data["duration_months"]),
            float(data["price"]),
            data.get("description", ""),
            data.get("features", "")
        ))
        conn.commit()
        return cursor.lastrowid


def create_subscription(data: Dict[str, Any]) -> int:
    with get_db() as conn:
        plan_id = int(data["plan_id"])
        plan = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        
        start_date = data.get("start_date") or date.today().isoformat()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        if data.get("end_date"):
            end_date = data["end_date"]
        else:
            duration = plan["duration_months"] if plan else 1
            end_dt = start_dt + timedelta(days=duration * 30)
            end_date = end_dt.isoformat()

        amount_paid = float(data.get("amount_paid") or (plan["price"] if plan else 0.0))

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscriptions (
                member_id, plan_id, start_date, end_date, amount_paid,
                payment_method, payment_status, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            int(data["member_id"]),
            plan_id,
            start_date,
            end_date,
            amount_paid,
            data.get("payment_method", "Cash"),
            data.get("payment_status", "paid"),
            "active",
            data.get("notes")
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_subscriptions(filter_status: str = "") -> List[Dict[str, Any]]:
    with get_db() as conn:
        query = """
            SELECT s.*, 
                   m.first_name, m.last_name, m.member_code, m.phone,
                   p.name as plan_name, p.duration_months
            FROM subscriptions s
            JOIN members m ON s.member_id = m.id
            JOIN plans p ON s.plan_id = p.id
            WHERE 1=1
        """
        params = []
        today = date.today().isoformat()
        seven_days_later = (date.today() + timedelta(days=7)).isoformat()

        if filter_status == "active":
            query += " AND s.end_date >= ?"
            params.append(today)
        elif filter_status == "expiring_soon":
            query += " AND s.end_date >= ? AND s.end_date <= ?"
            params.extend([today, seven_days_later])
        elif filter_status == "expired":
            query += " AND s.end_date < ?"
            params.append(today)

        query += " ORDER BY s.end_date DESC"
        rows = conn.execute(query, params).fetchall()
        result = []
        for r in rows:
            item = dict(r)
            end_d = datetime.strptime(item["end_date"], "%Y-%m-%d").date()
            delta = (end_d - date.today()).days
            item["days_remaining"] = delta
            if delta < 0:
                item["computed_status"] = "Expired"
                item["badge_color"] = "bg-rose-500/20 text-rose-400 border-rose-500/30"
            elif delta <= 7:
                item["computed_status"] = "Expiring Soon"
                item["badge_color"] = "bg-amber-500/20 text-amber-400 border-amber-500/30"
            else:
                item["computed_status"] = "Active"
                item["badge_color"] = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
            result.append(item)
        return result


def get_expiring_soon_subscriptions(days: int = 7) -> List[Dict[str, Any]]:
    with get_db() as conn:
        today = date.today().isoformat()
        future = (date.today() + timedelta(days=days)).isoformat()
        rows = conn.execute("""
            SELECT s.*, m.first_name, m.last_name, m.phone, m.member_code, p.name as plan_name
            FROM subscriptions s
            JOIN members m ON s.member_id = m.id
            JOIN plans p ON s.plan_id = p.id
            WHERE s.end_date >= ? AND s.end_date <= ?
            ORDER BY s.end_date ASC
        """, (today, future)).fetchall()
        res = []
        for r in rows:
            d = dict(r)
            end_d = datetime.strptime(d["end_date"], "%Y-%m-%d").date()
            d["days_remaining"] = (end_d - date.today()).days
            res.append(d)
        return res


# ---------------- ATTENDANCE ---------------- #

def check_in_member(member_id: int) -> Dict[str, Any]:
    with get_db() as conn:
        today = date.today().isoformat()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing = conn.execute("""
            SELECT id FROM attendance
            WHERE member_id = ? AND log_date = ? AND check_out_time IS NULL
        """, (member_id, today)).fetchone()

        if existing:
            return {"success": False, "message": "Member is already checked in right now."}

        conn.execute("""
            INSERT INTO attendance (member_id, check_in_time, log_date)
            VALUES (?, ?, ?)
        """, (member_id, now, today))
        conn.commit()
        return {"success": True, "message": "Member checked in successfully."}


def check_out_member(attendance_id: int) -> bool:
    with get_db() as conn:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("""
            UPDATE attendance SET check_out_time = ? WHERE id = ?
        """, (now, attendance_id))
        conn.commit()
        return True


def get_today_attendance() -> List[Dict[str, Any]]:
    with get_db() as conn:
        today = date.today().isoformat()
        rows = conn.execute("""
            SELECT a.*, m.first_name, m.last_name, m.member_code, m.avatar_url, m.phone
            FROM attendance a
            JOIN members m ON a.member_id = m.id
            WHERE a.log_date = ?
            ORDER BY a.check_in_time DESC
        """, (today,)).fetchall()
        return [dict(r) for r in rows]


# ---------------- DASHBOARD & ANALYTICS ---------------- #

def get_dashboard_metrics() -> Dict[str, Any]:
    with get_db() as conn:
        today = date.today().isoformat()
        seven_days = (date.today() + timedelta(days=7)).isoformat()
        first_of_month = date.today().replace(day=1).isoformat()

        total_members = conn.execute("SELECT COUNT(*) FROM members WHERE status = 'active'").fetchone()[0]
        active_subs = conn.execute("SELECT COUNT(*) FROM subscriptions WHERE end_date >= ?", (today,)).fetchone()[0]
        expiring_soon = conn.execute(
            "SELECT COUNT(*) FROM subscriptions WHERE end_date >= ? AND end_date <= ?",
            (today, seven_days)
        ).fetchone()[0]

        revenue_month = conn.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) FROM subscriptions WHERE start_date >= ?",
            (first_of_month,)
        ).fetchone()[0]

        total_revenue = conn.execute("SELECT COALESCE(SUM(amount_paid), 0) FROM subscriptions").fetchone()[0]
        today_checkins = conn.execute("SELECT COUNT(*) FROM attendance WHERE log_date = ?", (today,)).fetchone()[0]

        currently_in_gym = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE log_date = ? AND check_out_time IS NULL",
            (today,)
        ).fetchone()[0]

        transformation_highlights = []
        members_with_logs = conn.execute("""
            SELECT DISTINCT member_id FROM transformation_logs
        """).fetchall()

        for m_row in members_with_logs:
            m_id = m_row["member_id"]
            first_l = conn.execute(
                "SELECT weight_kg, log_date FROM transformation_logs WHERE member_id = ? ORDER BY log_date ASC LIMIT 1",
                (m_id,)
            ).fetchone()
            last_l = conn.execute(
                "SELECT weight_kg, log_date FROM transformation_logs WHERE member_id = ? ORDER BY log_date DESC LIMIT 1",
                (m_id,)
            ).fetchone()
            m_info = conn.execute("SELECT first_name, last_name, fitness_goal, avatar_url, member_code FROM members WHERE id = ?", (m_id,)).fetchone()

            if first_l and last_l and m_info and first_l["weight_kg"] != last_l["weight_kg"]:
                diff = round(last_l["weight_kg"] - first_l["weight_kg"], 1)
                transformation_highlights.append({
                    "id": m_id,
                    "name": f"{m_info['first_name']} {m_info['last_name']}".strip(),
                    "member_code": m_info["member_code"],
                    "avatar_url": m_info["avatar_url"],
                    "goal": m_info["fitness_goal"],
                    "initial_weight": first_l["weight_kg"],
                    "current_weight": last_l["weight_kg"],
                    "weight_change": diff,
                    "days": (datetime.strptime(last_l["log_date"], "%Y-%m-%d").date() - datetime.strptime(first_l["log_date"], "%Y-%m-%d").date()).days
                })

        transformation_highlights.sort(key=lambda x: abs(x["weight_change"]), reverse=True)

        recent_logs = conn.execute("""
            SELECT tl.*, m.first_name, m.last_name, m.member_code
            FROM transformation_logs tl
            JOIN members m ON tl.member_id = m.id
            ORDER BY tl.log_date DESC, tl.id DESC
            LIMIT 5
        """).fetchall()

        return {
            "total_members": total_members,
            "active_subscriptions": active_subs,
            "expiring_soon": expiring_soon,
            "revenue_month": round(revenue_month, 2),
            "total_revenue": round(total_revenue, 2),
            "today_checkins": today_checkins,
            "currently_in_gym": currently_in_gym,
            "transformation_highlights": transformation_highlights[:6],
            "recent_logs": [dict(r) for r in recent_logs]
        }
