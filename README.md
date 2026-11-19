# 🏋️ JUSTBEFIT - Gym Management & Transformation Suite

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/vinuthagopi24/JUSTBEFIT)

A full-stack, responsive web application engineered for gyms, fitness trainers, and clients. **JUSTBEFIT** tracks end-to-end gym administration: member registration, transformation milestones (body weight, BMI, body fat %, circumferences), subscription lifecycle tracking with automated renewal alerts, front-desk check-in attendance, and deep workout performance analysis.

---

## 🚀 One-Click Deploy to Render

Click the button below to deploy your live instance directly onto Render:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/vinuthagopi24/JUSTBEFIT)

Direct Blueprint Link: **[https://render.com/deploy?repo=https://github.com/vinuthagopi24/JUSTBEFIT](https://render.com/deploy?repo=https://github.com/vinuthagopi24/JUSTBEFIT)**

---

## 👥 Seeded Customers Roster
The system is pre-configured with the requested clients:
1. **Gopi** (`JBF-0001`) — Goal: Fat Loss & Conditioning (`94.5 kg` &rarr; `81.2 kg`, **-13.3 kg**)
2. **Vinutha** (`JBF-0002`) — Goal: Strength & Core Toning (`65.0 kg` &rarr; `59.5 kg`, **-5.5 kg**)
3. **Bhairav** (`JBF-0003`) — Goal: Hypertrophy / Clean Bulk (`68.0 kg` &rarr; `77.0 kg`, **+9.0 kg Muscle**)
4. **Acchu** (`JBF-0004`) — Goal: Functional Athletic Stamina & HIIT (`74.0 kg` &rarr; `68.0 kg`, **-6.0 kg**)
5. **Renuka** (`JBF-0005`) — Goal: Weight Loss & Posture Rehab (`78.5 kg` &rarr; `71.0 kg`, **-7.5 kg**)
6. **Shivanna** (`JBF-0006`) — Goal: Cardiovascular Health & Stamina (`86.0 kg` &rarr; `82.0 kg`, **-4.0 kg**)
7. **Rukmini** (`JBF-0007`) — Goal: Flexibility, Mobility & Lean Toning (`60.0 kg` &rarr; `56.2 kg`, **-3.8 kg**)
8. **Appaji** (`JBF-0008`) — Goal: Senior Wellness & Joint Mobility (`75.0 kg` &rarr; `73.5 kg`, **-1.5 kg**)

---

## ✨ Features

### 1. ⚡ New Customer Registration Section
- Dedicated **"+ Register New Customer"** section and button accessible across all screens:
  - Hero banner quick action & 10-second fast entry card
  - Sidebar prominent registration CTA
  - Top header one-click access
  - Comprehensive registration form capturing personal identity, baseline weight, body measurements, target goal, workout split, training intensity, nutrition protocol, and initial membership pass.

### 2. 🎨 Dark Aesthetic Gym Background & Glassmorphism
- High-definition dark gym photographic backgrounds featuring gym weights, barbells, moody atmospheric lighting, and neon emerald/cyan glows.
- Modern glassmorphism cards (`backdrop-blur-md bg-slate-900/80 border border-slate-800/80`) for clean readability and high aesthetic appeal.

### 3. 📊 Client Workout & Performance Analysis (`/analysis`)
- Comprehensive analysis engine showing how each client is working:
  - **Workout Consistency Meter**: 30-day attendance score (% and sessions completed)
  - **Assigned Workout Split**: e.g., Push/Pull/Legs (5x/wk), Bodybuilding Split (6x/wk), Kettlebell HIIT (4x/wk)
  - **Training Intensity**: High Resistance, Progressive Overload, Moderate, Senior-Safe
  - **Nutrition Protocol**: Target calories, macros, and diet notes
  - **Transformation Velocity**: Rate of progress in kg/month and goal completion %
  - **Trainer's Floor Assessment**: Direct head trainer evaluations of each client's discipline and form.

### 4. 📈 Transformation Trajectory & Measurements
- Weigh-in logging (kg), height, auto-calculated BMI with categories.
- Interactive Chart.js visualizer showing progression curves.
- Circumference tracking (chest, waist, hips, biceps, thighs).

### 5. 💳 Subscriptions & Check-in Desk
- Auto-calculated membership status: `Active`, `Expiring Soon` (7-day alert), and `Expired`.
- Front-desk QR / one-click check-in and check-out with live floor occupancy counter.
- CSV export for Members, Subscriptions, and Transformation data.

---

## 🚀 How to Run Locally

```powershell
cd "C:\Users\Dell\.gemini\antigravity\scratch\JUSTBEFIT"
python serve.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser!
