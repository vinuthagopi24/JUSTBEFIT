import os
from datetime import date, timedelta
from database import init_db, get_db, DB_PATH

def seed():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print("Removed old database for fresh seed.")
        except Exception as e:
            print(f"Notice: {e}")

    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        print("Seeding membership plans...")

        # 1. Plans
        plans = [
            ("Monthly Starter", 1, 49.00, "Standard gym floor access, cardio equipment & locker.", "Cardio + Weights, Locker Access, Free Water"),
            ("Quarterly Pro", 3, 129.00, "Full access to gym, group fitness classes, and free sauna.", "All Gym Equipment, Group Classes, Sauna, 1 Free PT Session"),
            ("Transformation 6-Month", 6, 239.00, "Dedicated transformation package with monthly nutrition audit and measurement checks.", "Full Access, Bi-weekly Body Composition Scan, Custom Diet Chart, Steam & Sauna"),
            ("Annual Elite VIP", 12, 420.00, "365 days of unlimited access, personal locker, priority trainer booking, towel service.", "All-Inclusive VIP, Unlimited Classes, Locker, Towel Service, 4 Free Guest Passes"),
            ("Personal Training Addon", 3, 349.00, "1-on-1 dedicated coach 3x/week + customized macro-nutrient meal plan.", "Private Coach 3x/Week, Custom Macro Plan, Weekly Progress Review")
        ]

        cursor.executemany("""
            INSERT INTO plans (name, duration_months, price, description, features)
            VALUES (?, ?, ?, ?, ?)
        """, plans)

        print("Seeding clients: Gopi, Vinutha, Bhairav, Acchu, Renuka, Shivanna, Rukmini, Appaji with authentic Indian faces...")
        today = date.today()

        # Exact names without any suffix or prefix
        members_data = [
            {
                "code": "JBF-0001",
                "first": "Gopi", "last": "",
                "email": "gopi@justbefit.com", "phone": "+91 98450 12345",
                "gender": "Male", "dob": "1994-06-15",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98450 99999",
                "join_date": (today - timedelta(days=120)).isoformat(),
                "target_weight": 80.0, "height_cm": 178.0,
                "fitness_goal": "Fat Loss & Athletic Conditioning",
                "workout_split": "Push / Pull / Legs (5x/week)",
                "workout_intensity": "High Intensity Resistance",
                "nutrition_plan": "High Protein Caloric Deficit (2,100 kcal)",
                "trainer_assessment": "Exceptional work ethic. Shows up at 6:30 AM without fail. Progressive overload on bench and squats is steadily rising.",
                "medical_notes": "Mild lower back stiffness from desk work. Doing daily hip mobility warm-ups.",
                "avatar_url": "https://images.unsplash.com/photo-1607346256330-dee7af15f7c5?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0002",
                "first": "Vinutha", "last": "",
                "email": "vinutha@justbefit.com", "phone": "+91 98451 23456",
                "gender": "Female", "dob": "1996-09-21",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98451 00000",
                "join_date": (today - timedelta(days=90)).isoformat(),
                "target_weight": 58.0, "height_cm": 165.0,
                "fitness_goal": "Strength & Core Toning",
                "workout_split": "Upper / Lower Split (4x/week)",
                "workout_intensity": "Moderate-High Resistance",
                "nutrition_plan": "Balanced Macros + Post-Workout Whey (1,650 kcal)",
                "trainer_assessment": "Great consistency. Achieved first 3 unassisted pull-ups this month. Core stabilization is markedly improved.",
                "medical_notes": "None reported. Excellent cardiovascular recovery.",
                "avatar_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0003",
                "first": "Bhairav", "last": "",
                "email": "bhairav@justbefit.com", "phone": "+91 98452 34567",
                "gender": "Male", "dob": "1999-03-11",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98452 11111",
                "join_date": (today - timedelta(days=105)).isoformat(),
                "target_weight": 78.0, "height_cm": 180.0,
                "fitness_goal": "Hypertrophy / Clean Bulk",
                "workout_split": "Heavy Bodybuilding Split (6x/week)",
                "workout_intensity": "Maximum Progressive Overload",
                "nutrition_plan": "Clean Caloric Surplus (3,100 kcal, 180g Protein)",
                "trainer_assessment": "Gained 9 kg of solid mass. Squat PR at 120 kg. Needs to monitor form on heavy overhead presses to protect shoulders.",
                "medical_notes": "Past right shoulder strain. Strict rotator cuff activation before pressing.",
                "avatar_url": "https://images.unsplash.com/photo-1566492031773-4f4e44671857?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0004",
                "first": "Acchu", "last": "",
                "email": "acchu@justbefit.com", "phone": "+91 98453 45678",
                "gender": "Male", "dob": "1997-12-05",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98453 22222",
                "join_date": (today - timedelta(days=80)).isoformat(),
                "target_weight": 67.0, "height_cm": 172.0,
                "fitness_goal": "Functional Athletic Stamina & HIIT",
                "workout_split": "Kettlebell & Functional Cross-Training (4x/week)",
                "workout_intensity": "High-Intensity Interval Circuit",
                "nutrition_plan": "High Carb Endurance Regimen (2,400 kcal)",
                "trainer_assessment": "Cardio engine is outstanding. 5km treadmill time cut by 3 minutes. Explosive power in box jumps and battle ropes is top tier.",
                "medical_notes": "None.",
                "avatar_url": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0005",
                "first": "Renuka", "last": "",
                "email": "renuka@justbefit.com", "phone": "+91 98454 56789",
                "gender": "Female", "dob": "1991-08-19",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98454 33333",
                "join_date": (today - timedelta(days=75)).isoformat(),
                "target_weight": 68.0, "height_cm": 162.0,
                "fitness_goal": "Weight Loss & Posture Rehab",
                "workout_split": "Low-Impact Resistance & Core Rehab (3x/week)",
                "workout_intensity": "Moderate Intensity / High Volume",
                "nutrition_plan": "Whole-Food Caloric Deficit (1,550 kcal)",
                "trainer_assessment": "Steadily losing waist circumference (-7cm). Daily step count consistently exceeds 10,000 steps.",
                "medical_notes": "Patellofemoral knee discomfort. Box squats instead of deep barbell squats.",
                "avatar_url": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0006",
                "first": "Shivanna", "last": "",
                "email": "shivanna@justbefit.com", "phone": "+91 98455 67890",
                "gender": "Male", "dob": "1985-04-14",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98455 44444",
                "join_date": (today - timedelta(days=60)).isoformat(),
                "target_weight": 80.0, "height_cm": 176.0,
                "fitness_goal": "Cardiovascular Health & Stamina",
                "workout_split": "Full Body Machine Circuit & Incline Walk (4x/week)",
                "workout_intensity": "Moderate Cardiovascular Training",
                "nutrition_plan": "Heart-Healthy Mediterranean Diet (2,200 kcal)",
                "trainer_assessment": "Resting heart rate dropped from 78 to 68 bpm. Very disciplined with post-workout cool-downs.",
                "medical_notes": "Mild hypertension, cleared by cardiologist for regular moderate gym activity.",
                "avatar_url": "https://images.unsplash.com/photo-1595152772835-219674b2a8a6?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0007",
                "first": "Rukmini", "last": "",
                "email": "rukmini@justbefit.com", "phone": "+91 98456 78901",
                "gender": "Female", "dob": "1998-02-28",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98456 55555",
                "join_date": (today - timedelta(days=50)).isoformat(),
                "target_weight": 54.0, "height_cm": 160.0,
                "fitness_goal": "Flexibility, Mobility & Lean Toning",
                "workout_split": "Resistance Bands, Pilates & Light Dumbbells (4x/week)",
                "workout_intensity": "Moderate Dynamic Resistance",
                "nutrition_plan": "High Fiber & Lean Protein (1,500 kcal)",
                "trainer_assessment": "Significant flexibility improvements in hamstrings and thoracic spine. Very punctual.",
                "medical_notes": "None.",
                "avatar_url": "https://images.unsplash.com/photo-1614283233556-f35b0c801ef1?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            },
            {
                "code": "JBF-0008",
                "first": "Appaji", "last": "",
                "email": "appaji@justbefit.com", "phone": "+91 98457 89012",
                "gender": "Male", "dob": "1968-11-10",
                "emergency_contact": "Family Contact", "emergency_phone": "+91 98457 66666",
                "join_date": (today - timedelta(days=40)).isoformat(),
                "target_weight": 72.0, "height_cm": 170.0,
                "fitness_goal": "Senior Wellness, Balance & Joint Mobility",
                "workout_split": "Mobility Drills, Cable Pulls & Treadmill Walk (3x/week)",
                "workout_intensity": "Gentle-Moderate Joint-Safe Routine",
                "nutrition_plan": "Anti-Inflammatory Nutrient-Dense Plan (1,900 kcal)",
                "trainer_assessment": "Balance and knee stability improved tremendously. Able to walk 45 minutes on treadmill with zero joint pain.",
                "medical_notes": "Mild osteoarthritis in left knee. Avoid jumping and heavy impact.",
                "avatar_url": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300&auto=format&fit=crop&q=80",
                "status": "active"
            }
        ]

        for m in members_data:
            cursor.execute("""
                INSERT INTO members (
                    member_code, first_name, last_name, email, phone, gender,
                    dob, emergency_contact, emergency_phone, join_date,
                    target_weight, height_cm, fitness_goal, workout_split,
                    workout_intensity, nutrition_plan, trainer_assessment,
                    medical_notes, avatar_url, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                m["code"], m["first"], m["last"], m["email"], m["phone"], m["gender"],
                m["dob"], m["emergency_contact"], m["emergency_phone"], m["join_date"],
                m["target_weight"], m["height_cm"], m["fitness_goal"], m["workout_split"],
                m["workout_intensity"], m["nutrition_plan"], m["trainer_assessment"],
                m["medical_notes"], m["avatar_url"], m["status"]
            ))

        print("Seeding transformation measurement timelines for all 8 clients...")

        # 1. Gopi: 94.5 kg -> 81.2 kg (-13.3 kg)
        gopi_logs = [
            (1, (today - timedelta(days=120)).isoformat(), 94.5, 178.0, 29.8, 30.5, 32.0, 110.0, 104.0, 106.0, 35.0, 62.0, "Day 1 Registration baseline with trainer."),
            (1, (today - timedelta(days=95)).isoformat(), 91.0, 178.0, 28.7, 28.0, 33.0, 108.0, 99.5, 104.0, 35.5, 61.0, "Down 3.5kg. Energy levels high."),
            (1, (today - timedelta(days=70)).isoformat(), 87.5, 178.0, 27.6, 25.5, 34.2, 106.0, 95.0, 102.0, 36.0, 59.5, "Clothes fitting much looser, waist down 9cm."),
            (1, (today - timedelta(days=45)).isoformat(), 84.8, 178.0, 26.8, 23.0, 35.5, 104.5, 91.0, 100.0, 36.5, 58.5, "Hit 90kg bench press PR."),
            (1, (today - timedelta(days=15)).isoformat(), 82.5, 178.0, 26.0, 21.0, 36.5, 103.0, 88.0, 98.0, 37.0, 57.5, "Visible abdominal definition appearing."),
            (1, today.isoformat(), 81.2, 178.0, 25.6, 20.0, 37.0, 102.0, 86.0, 97.0, 37.5, 57.0, "Current check-in! Down 13.3 kg total.")
        ]

        # 2. Vinutha: 65.0 kg -> 59.5 kg (-5.5 kg)
        vinutha_logs = [
            (2, (today - timedelta(days=90)).isoformat(), 65.0, 165.0, 23.9, 28.0, 25.5, 89.0, 78.0, 99.0, 26.0, 57.0, "Day 1 Baseline."),
            (2, (today - timedelta(days=60)).isoformat(), 63.0, 165.0, 23.1, 25.5, 26.5, 87.5, 75.0, 97.0, 27.0, 56.0, "First unassisted pull-up achieved!"),
            (2, (today - timedelta(days=30)).isoformat(), 61.0, 165.0, 22.4, 23.0, 27.5, 86.5, 72.0, 95.0, 27.5, 55.0, "Consistent 4x/week lifting sessions."),
            (2, today.isoformat(), 59.5, 165.0, 21.9, 21.0, 28.5, 86.0, 69.5, 93.5, 28.0, 54.0, "Target weight reached! Waist down 8.5 cm.")
        ]

        # 3. Bhairav: 68.0 kg -> 77.0 kg (+9.0 kg Muscle)
        bhairav_logs = [
            (3, (today - timedelta(days=105)).isoformat(), 68.0, 180.0, 21.0, 12.0, 34.0, 95.0, 78.0, 92.0, 31.0, 52.0, "Starting lean muscle surplus."),
            (3, (today - timedelta(days=70)).isoformat(), 71.5, 180.0, 22.1, 12.5, 35.5, 98.0, 79.0, 94.0, 33.0, 54.0, "Squat up to 100kg."),
            (3, (today - timedelta(days=35)).isoformat(), 74.5, 180.0, 23.0, 13.0, 37.0, 102.0, 80.5, 96.0, 35.0, 56.0, "Arms and back developing fast."),
            (3, today.isoformat(), 77.0, 180.0, 23.8, 13.5, 38.5, 105.0, 82.0, 98.0, 36.5, 57.5, "Up 9.0kg of solid muscle! Arms up 5.5cm.")
        ]

        # 4. Acchu: 74.0 kg -> 68.0 kg (-6.0 kg)
        acchu_logs = [
            (4, (today - timedelta(days=80)).isoformat(), 74.0, 172.0, 25.0, 24.0, 29.0, 98.0, 86.0, 98.0, 30.0, 56.0, "Baseline check."),
            (4, (today - timedelta(days=40)).isoformat(), 71.0, 172.0, 24.0, 21.0, 30.0, 97.0, 82.0, 96.0, 30.5, 55.0, "Agility and sprint recovery high."),
            (4, today.isoformat(), 68.0, 172.0, 23.0, 18.0, 31.5, 96.0, 78.5, 94.0, 31.0, 54.0, "Lean and athletic. 6kg dropped.")
        ]

        # 5. Renuka: 78.5 kg -> 71.0 kg (-7.5 kg)
        renuka_logs = [
            (5, (today - timedelta(days=75)).isoformat(), 78.5, 162.0, 29.9, 34.0, 24.0, 100.0, 92.0, 108.0, 29.0, 62.0, "Baseline check."),
            (5, (today - timedelta(days=40)).isoformat(), 74.5, 162.0, 28.4, 31.0, 25.0, 97.0, 87.0, 104.0, 28.5, 60.0, "Knee pain reduced, walking briskly."),
            (5, today.isoformat(), 71.0, 162.0, 27.1, 28.0, 26.5, 94.0, 83.0, 101.0, 28.0, 58.0, "Down 7.5kg! Clothes fitting comfortably.")
        ]

        # 6. Shivanna: 86.0 kg -> 82.0 kg (-4.0 kg)
        shivanna_logs = [
            (6, (today - timedelta(days=60)).isoformat(), 86.0, 176.0, 27.8, 28.0, 28.0, 104.0, 98.0, 104.0, 33.0, 60.0, "Baseline check."),
            (6, (today - timedelta(days=30)).isoformat(), 84.0, 176.0, 27.1, 26.5, 29.0, 103.0, 95.0, 102.0, 33.5, 59.0, "Blood pressure normalized."),
            (6, today.isoformat(), 82.0, 176.0, 26.5, 25.0, 30.0, 101.5, 93.0, 100.5, 34.0, 58.5, "Down 4.0kg. Stamina vastly improved.")
        ]

        # 7. Rukmini: 60.0 kg -> 56.2 kg (-3.8 kg)
        rukmini_logs = [
            (7, (today - timedelta(days=50)).isoformat(), 60.0, 160.0, 23.4, 26.0, 24.0, 84.0, 74.0, 94.0, 24.0, 53.0, "Baseline check."),
            (7, today.isoformat(), 56.2, 160.0, 22.0, 22.5, 25.5, 83.0, 68.0, 91.0, 24.5, 51.5, "Toned waist (-6cm) and strong posture.")
        ]

        # 8. Appaji: 75.0 kg -> 73.5 kg (-1.5 kg)
        appaji_logs = [
            (8, (today - timedelta(days=40)).isoformat(), 75.0, 170.0, 26.0, 26.0, 26.0, 98.0, 92.0, 98.0, 30.0, 56.0, "Baseline check."),
            (8, today.isoformat(), 73.5, 170.0, 25.4, 24.5, 27.0, 97.0, 89.0, 96.5, 30.5, 55.0, "Joint stiffness gone. Walks with ease.")
        ]

        all_logs = gopi_logs + vinutha_logs + bhairav_logs + acchu_logs + renuka_logs + shivanna_logs + rukmini_logs + appaji_logs
        cursor.executemany("""
            INSERT INTO transformation_logs (
                member_id, log_date, weight_kg, height_cm, bmi,
                body_fat_pct, muscle_mass_pct, chest_cm, waist_cm,
                hips_cm, bicep_cm, thigh_cm, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, all_logs)

        # 3. Subscriptions for all 8 clients
        print("Seeding subscriptions...")
        subscriptions_data = [
            (1, 3, (today - timedelta(days=120)).isoformat(), (today + timedelta(days=60)).isoformat(), 239.00, "Credit Card", "paid", "active", "6-Month Transformation package"),
            (2, 4, (today - timedelta(days=90)).isoformat(), (today + timedelta(days=275)).isoformat(), 420.00, "UPI / Online", "paid", "active", "Annual VIP Membership"),
            (3, 5, (today - timedelta(days=105)).isoformat(), (today + timedelta(days=45)).isoformat(), 349.00, "Debit Card", "paid", "active", "Personal Trainer 3x weekly"),
            (4, 2, (today - timedelta(days=86)).isoformat(), (today + timedelta(days=4)).isoformat(), 129.00, "Cash", "paid", "active", "Expires in 4 days - Renewal reminder sent"),
            (5, 2, (today - timedelta(days=75)).isoformat(), (today + timedelta(days=15)).isoformat(), 129.00, "UPI / Online", "paid", "active", "Quarterly renewal upcoming"),
            (6, 1, (today - timedelta(days=25)).isoformat(), (today + timedelta(days=5)).isoformat(), 49.00, "Cash", "paid", "active", "Monthly pass renew soon"),
            (7, 2, (today - timedelta(days=50)).isoformat(), (today + timedelta(days=40)).isoformat(), 129.00, "UPI / Online", "paid", "active", "Quarterly plan active"),
            (8, 1, (today - timedelta(days=33)).isoformat(), (today - timedelta(days=3)).isoformat(), 49.00, "Cash", "paid", "expired", "Expired pass - renewal follow-up")
        ]

        cursor.executemany("""
            INSERT INTO subscriptions (
                member_id, plan_id, start_date, end_date, amount_paid,
                payment_method, payment_status, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, subscriptions_data)

        # 4. Realistic Attendance for all 8 clients
        print("Seeding attendance records for workout consistency tracking...")
        now_time = today.isoformat()

        attendance_records = []
        # Gopi attended 22 times
        for d in range(1, 28, 2):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((1, f"{past_d} 06:30:00", f"{past_d} 07:45:00", past_d))
        # Vinutha attended 18 times
        for d in range(1, 28, 3):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((2, f"{past_d} 07:00:00", f"{past_d} 08:15:00", past_d))
        # Bhairav attended 24 times
        for d in range(1, 28):
            if d % 7 != 0:
                past_d = (today - timedelta(days=d)).isoformat()
                attendance_records.append((3, f"{past_d} 18:00:00", f"{past_d} 19:30:00", past_d))
        # Acchu attended 16 times
        for d in range(1, 28, 3):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((4, f"{past_d} 17:30:00", f"{past_d} 18:45:00", past_d))
        # Renuka attended 12 times
        for d in range(2, 28, 4):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((5, f"{past_d} 10:00:00", f"{past_d} 11:00:00", past_d))
        # Shivanna attended 15 times
        for d in range(1, 28, 3):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((6, f"{past_d} 06:00:00", f"{past_d} 07:10:00", past_d))
        # Rukmini attended 14 times
        for d in range(2, 28, 3):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((7, f"{past_d} 08:00:00", f"{past_d} 09:00:00", past_d))
        # Appaji attended 10 times
        for d in range(3, 28, 4):
            past_d = (today - timedelta(days=d)).isoformat()
            attendance_records.append((8, f"{past_d} 07:30:00", f"{past_d} 08:30:00", past_d))

        # Today's checkins: Gopi, Vinutha, Bhairav, Acchu
        attendance_records.append((1, f"{now_time} 06:30:00", f"{now_time} 07:45:00", today.isoformat()))
        attendance_records.append((2, f"{now_time} 07:15:00", None, today.isoformat()))
        attendance_records.append((3, f"{now_time} 08:00:00", None, today.isoformat()))
        attendance_records.append((4, f"{now_time} 08:30:00", None, today.isoformat()))

        cursor.executemany("""
            INSERT INTO attendance (member_id, check_in_time, check_out_time, log_date)
            VALUES (?, ?, ?, ?)
        """, attendance_records)

        conn.commit()
        print("Database seeded with exact names: Gopi, Vinutha, Bhairav, Acchu, Renuka, Shivanna, Rukmini, Appaji and Indian faces!")

if __name__ == "__main__":
    seed()
