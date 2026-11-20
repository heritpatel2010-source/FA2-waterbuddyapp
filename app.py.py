import streamlit as st
from datetime import date, datetime
import json
from pathlib import Path

st.set_page_config(page_title="WaterBuddy", page_icon="💧", layout="wide")

BG = "#F4F8FF"
DEFAULT_GOALS = {"Child": 1500, "Teen": 2000, "Adult": 2000, "Senior": 1800}
TIPS = {
    "Child": ("🧸", "Make water breaks fun", "Keep water nearby during play and study. Ask a trusted adult about your hydration needs."),
    "Teen": ("🎒", "Hydrate around your routine", "Keep a reusable bottle handy during school, study sessions and activities."),
    "Adult": ("🌿", "Build a simple habit", "Pair water breaks with everyday routines, such as meals or desk breaks."),
    "Senior": ("☀️", "Remember regular sips", "Follow any clinician's fluid guidance."),
}

st.markdown("""
<style>
.stApp { background: #F4F8FF; color: #182B4B; }
.block-container { max-width: 1180px; padding-top: 1.4rem; }
.wb-header { background: #07152F; color: white; padding: 22px 28px; border-radius: 18px 18px 0 0; }
.wb-hero { background: #07152F; color: white; padding: 12px 30px 30px; border-radius: 0 0 18px 18px; margin-bottom: 22px; }
.wb-hero h1 { color: white; font-size: 2.55rem; line-height: 1.1; margin: 8px 0; }
.wb-hero p { color: #C0CEE8; }
.stat { background: white; border: 1px solid #E6EDF7; border-radius: 16px; padding: 17px 19px; min-height: 112px; }
.stat-label { color: #8191AA; font-size: .78rem; font-weight: 700; }
.stat-value { font-size: 1.75rem; font-weight: 800; margin-top: 8px; }
.panel { background: white; border: 1px solid #E6EDF7; border-radius: 16px; padding: 20px; margin-bottom: 16px; }
.small-muted { color: #8191AA; font-size: .9rem; }
.bottle-wrap { display:flex; align-items:center; gap:24px; }
.bottle { width:76px; height:150px; border:5px solid #C7E2FF; border-radius:18px 18px 22px 22px; position:relative; overflow:hidden; background:#EFF8FF; }
.bottle:before { content:''; position:absolute; width:30px; height:13px; top:-13px; left:18px; border:4px solid #C7E2FF; background:#EFF8FF; border-radius:5px; }
.bottle-fill { position:absolute; bottom:0; left:0; right:0; background:linear-gradient(0deg,#45C8F3,#8DEBFF); }
div.stButton > button { border-radius: 11px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# Session state: Streamlit Cloud is a web host, so data is kept for this browser session.
if "day" not in st.session_state or st.session_state.day != date.today().isoformat():
    st.session_state.day = date.today().isoformat()
    st.session_state.entries = []
    if "age_group" not in st.session_state:
        st.session_state.age_group = "Teen"
    if "goal" not in st.session_state:
        st.session_state.goal = DEFAULT_GOALS[st.session_state.age_group]
if "entries" not in st.session_state:
    st.session_state.entries = []
if "age_group" not in st.session_state:
    st.session_state.age_group = "Teen"
if "goal" not in st.session_state:
    st.session_state.goal = DEFAULT_GOALS[st.session_state.age_group]


def add_water(amount):
    if 1 <= int(amount) <= 5000:
        st.session_state.entries.append({"amount": int(amount), "time": datetime.now().strftime("%I:%M %p")})


def total_water():
    return sum(x["amount"] for x in st.session_state.entries)

amount = total_water()
goal = int(st.session_state.goal)
percent = round(amount / goal * 100) if goal else 0
remaining = max(0, goal - amount)

st.markdown('<div class="wb-header"><h2 style="margin:0;color:white">💧 WaterBuddy <span style="font-size:.8rem;color:#9DB8E7">&nbsp; YOUR DAILY HYDRATION COMPANION</span></h2></div>', unsafe_allow_html=True)
st.markdown(f'''<div class="wb-hero"><div style="color:#56DDF4;font-weight:800;letter-spacing:1px">A LITTLE WATER, A BETTER DAY</div><h1>Make hydration<br>your superpower.</h1><p>Track your water, celebrate small wins, and take your day one sip at a time.</p><div style="font-size:2.3rem">💧</div><div style="color:#9DB8E7">{date.today().strftime('%A, %d %B %Y')}</div></div>''', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, label, value, color in [
    (c1, "💧 WATER DRUNK", f"{amount:,} ml", "#2879FF"),
    (c2, "🎯 REMAINING", f"{remaining:,} ml", "#182B4B"),
    (c3, "⚡ COMPLETED", f"{percent}%", "#13B887"),
]:
    with col:
        st.markdown(f'<div class="stat"><div class="stat-label">{label}</div><div class="stat-value" style="color:{color}">{value}</div></div>', unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.15, .85], gap="large")
with left:
    st.markdown('<div class="panel"><h3>💧 Your hydration progress</h3><p class="small-muted">Watch your bottle fill as you drink.</p></div>', unsafe_allow_html=True)
    fill = min(100, percent)
    status = "Fresh start!" if amount == 0 else "Nice beginning!" if percent < 25 else "You're on your way!" if percent < 50 else "Look at you go!" if percent < 75 else "So close!" if percent < 100 else "Goal achieved!"
    message = "Every journey begins with one sip. Let's get started." if amount == 0 else "Small actions build habits. Keep water nearby." if percent < 25 else "A lovely start. Keep it steady." if percent < 50 else "You've crossed the halfway mark. Keep it comfortable." if percent < 75 else f"{remaining:,} ml remaining. No need to rush." if percent < 100 else "Wonderful! Keep listening to your body's needs."
    st.markdown(f'''<div class="panel"><div class="bottle-wrap"><div class="bottle"><div class="bottle-fill" style="height:{fill}%"></div></div><div><div style="font-size:2.1rem;font-weight:800;color:#2879FF">{percent}%</div><b>{status}</b><p class="small-muted">{message}</p></div></div>''', unsafe_allow_html=True)
    st.progress(min(100, percent) / 100)
    st.caption(f"{amount:,} ml consumed  ·  Goal: {goal:,} ml")
    st.markdown("**Log a drink**")
    st.caption("Choose an amount to add to today's total.")
    q1, q2, q3 = st.columns(3)
    for col, ml, label in [(q1, 150, "🥛 Small glass"), (q2, 250, "💧 One glass"), (q3, 500, "🫗 Large bottle")]:
        with col:
            if st.button(f"{label}\n{ml} ml", use_container_width=True, key=f"quick{ml}"):
                add_water(ml)
                st.rerun()
    custom_col, add_col = st.columns([2, 1])
    with custom_col:
        custom = st.number_input("Custom amount (ml)", min_value=1, max_value=5000, value=250, step=1)
    with add_col:
        st.write("")
        st.write("")
        if st.button("＋ Add water", type="primary", use_container_width=True):
            add_water(custom)
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel"><h3>🧾 Today\'s drink history</h3></div>', unsafe_allow_html=True)
    if not st.session_state.entries:
        st.info("💧 Your first glass will appear here.")
    else:
        for i, entry in enumerate(reversed(st.session_state.entries)):
            st.write(f"🥛 **Water intake** {'· Latest' if i == 0 else ''} — {entry['time']}  |  **+{entry['amount']:,} ml**")
    if st.button("↶ Undo last entry", disabled=not st.session_state.entries):
        st.session_state.entries.pop()
        st.rerun()

with right:
    st.markdown('<div class="panel"><h3>🎯 Your daily goal</h3><p class="small-muted">Choose an age group and set your own tracking target.</p></div>', unsafe_allow_html=True)
    age = st.selectbox("Age group", list(DEFAULT_GOALS), index=list(DEFAULT_GOALS).index(st.session_state.age_group))
    if age != st.session_state.age_group:
        st.session_state.age_group = age
        st.session_state.goal = DEFAULT_GOALS[age]
        st.rerun()
    new_goal = st.number_input("Daily goal (ml)", min_value=250, max_value=10000, value=int(st.session_state.goal), step=50)
    if st.button("Save goal", type="primary"):
        st.session_state.goal = int(new_goal)
        st.rerun()
    st.caption(f"Suggested starting point: {DEFAULT_GOALS[age]:,} ml. Editable target.")
    tip = TIPS[age]
    st.info(f"{tip[0]} **{tip[1]}**\n\n{tip[2]}")
    st.caption("Hydration needs vary. This tracker is for habit tracking, not medical advice.")

    if percent >= 100:
        win = ("🏆", "Goal reached!", "You reached your selected goal.")
    elif percent >= 75:
        win = ("🚀", "Final stretch!", "You're at least 75% there. Stay comfortable.")
    elif percent >= 50:
        win = ("🏅", "Halfway hero!", "Celebrate your progress.")
    elif percent >= 25:
        win = ("⭐", "Quarter-way champion!", "You've reached at least 25% of your chosen goal.")
    elif amount > 0:
        win = ("🌱", "First sip logged!", "You've taken the first step.")
    else:
        win = ("🌊", "Your journey starts here", "Log your first drink to begin collecting little wins.")
    st.markdown('<div class="panel"><h3>✨ Little wins</h3></div>', unsafe_allow_html=True)
    st.success(f"{win[0]} **{win[1]}**\n\n{win[2]}")
    if st.button("↻ Reset today's tracker", use_container_width=True):
        st.session_state.entries = []
        st.rerun()

st.markdown("<hr><p style='text-align:center;color:#8191AA'>Made with 💙 for healthier everyday habits. WaterBuddy · Sip smart, feel good.</p>", unsafe_allow_html=True)

# Export today's history so users can keep a copy between sessions/deployments.
if st.session_state.entries:
    export_data = {"date": date.today().isoformat(), "age_group": st.session_state.age_group, "goal_ml": st.session_state.goal, "entries": st.session_state.entries}
    st.download_button("⬇ Download today's water history (JSON)", json.dumps(export_data, indent=2), file_name="waterbuddy_history.json", mime="application/json")
