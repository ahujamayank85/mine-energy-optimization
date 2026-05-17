import streamlit as st

st.set_page_config(page_title="Mining RMR Calculator", page_icon="⛏️")

st.title("⛏️ Underground Coal Mine RMR App")
st.markdown("Developed for Engineering & Rock Mechanics Assessment")

with st.sidebar:
    st.header("Input Parameters")
    ucs = st.number_input("UCS of Rock (MPa)", min_value=0.0, value=50.0)
    rqd = st.slider("RQD (%)", 0, 100, 75)
    spacing = st.number_input("Joint Spacing (mm)", min_value=0, value=250)
    
    cond = st.selectbox("Joint Condition", 
                        options=[(30, "Rough/Unweathered"), (20, "Smooth"), (10, "Slickensided")],
                        format_func=lambda x: x[1])
    
    water = st.selectbox("Groundwater Condition", 
                         options=[(15, "Dry"), (10, "Damp"), (7, "Wet"), (0, "Flowing")],
                         format_func=lambda x: x[1])

    st.header("Adjustments")
    orient = st.selectbox("Joint Orientation Adjustment", 
                          options=[(0, "Very Favorable"), (-2, "Favorable"), (-5, "Fair"), (-10, "Unfavorable"), (-12, "Very Unfavorable")],
                          format_func=lambda x: x[1])

# --- Calculations ---
r1 = 15 if ucs > 100 else 12 if ucs >= 50 else 7 if ucs >= 25 else 4
r2 = 20 if rqd > 90 else 17 if rqd >= 75 else 13 if rqd >= 50 else 8 if rqd >= 25 else 3
r3 = 20 if spacing > 2000 else 15 if spacing >= 600 else 10 if spacing >= 200 else 8 if spacing >= 60 else 5
r4 = cond[0]
r5 = water[0]
adj = orient[0]

final_rmr = r1 + r2 + r3 + r4 + r5 + adj

# --- Results Display ---
st.header(f"Final Adjusted RMR: {final_rmr}")

if final_rmr > 60:
    st.success("ROCK CLASS: GOOD (Class II/I)")
    st.write("**Support:** Systematic bolting 1.2m - 1.5m spacing.")
elif final_rmr > 40:
    st.warning("ROCK CLASS: FAIR (Class III)")
    st.write("**Support:** Bolting at 1.0m - 1.2m + W-Straps/Mesh.")
else:
    st.error("ROCK CLASS: POOR/VERY POOR (Class IV/V)")
    st.write("**Support:** Immediate steel sets, heavy bolting, or restricted entry.")

st.info("Note: This follows CMRI-RMR standards for Indian Coal Mines.")