import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from frontend.utils.api_client import set_risk_profile, get_me, get_advice, get_advice_history

st.title("AI Financial Advisor")

if not st.session_state.get("token"):
    st.warning("Please log in from the Home page.")
    st.stop()

token = st.session_state.token
user = st.session_state.user

# --- Risk questionnaire ---
st.subheader("Risk Profile Questionnaire")

if user.get("risk_score"):
    from backend.models.risk import risk_label
    score = user["risk_score"]
    label = risk_label(score)
    st.success(f"Your current risk profile: **{label}** (score {score}/68)")
    if st.button("Retake questionnaire"):
        user["risk_score"] = None

if not user.get("risk_score"):
    st.markdown(
        "Answer these questions honestly — they determine your investment recommendations. "
        "All information is treated confidentially."
    )

    with st.form("risk_form"):

        # ── Section A ────────────────────────────────────────────────────────
        st.markdown("### Section A — Financial Situation (Risk Capacity)")
        st.caption(
            "Measures your objective ability to bear financial risk. "
            "Carries the greatest weight; in case of divergence with Section C the more conservative answer prevails."
        )

        a1 = st.radio(
            "A1. Annual net income",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Up to €30,000",
                2: "€30,001 – €70,000",
                3: "€70,001 – €150,000",
                4: "Over €150,000",
            }[x],
        )

        a2 = st.radio(
            "A2. Total net wealth (financial + real estate + business interests)",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Up to €100,000",
                2: "€100,001 – €500,000",
                3: "€500,001 – €2,000,000",
                4: "Over €2,000,000",
            }[x],
        )

        a3 = st.radio(
            "A3. Amount you intend to invest",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Up to €10,000",
                2: "€10,001 – €50,000",
                3: "€50,001 – €200,000",
                4: "Over €200,000",
            }[x],
        )

        a4 = st.radio(
            "A4. What percentage of your total financial wealth does this investment represent?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "More than 75%",
                2: "50% – 75%",
                3: "25% – 49%",
                4: "Less than 25%",
            }[x],
        )

        a5 = st.radio(
            "A5. Current level of debt or financial liabilities",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Significant (>50% of annual income)",
                2: "Moderate (20% – 50%)",
                3: "Limited (<20%)",
                4: "None",
            }[x],
        )

        a6 = st.radio(
            "A6. How often do you expect to withdraw funds from this investment?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Frequently (monthly / quarterly)",
                2: "Occasionally (once or twice a year)",
                3: "Rarely (every few years)",
                4: "Not until the planned end of the investment",
            }[x],
        )

        a7 = st.radio(
            "A7. If this investment lost 30% of its value, to what extent would it compromise your standard of living?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Severely",
                2: "Moderately",
                3: "Slightly",
                4: "Not at all",
            }[x],
        )

        a8 = st.radio(
            "A8. Do you maintain emergency savings outside this investment?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "None",
                2: "Less than 3 months of expenses",
                3: "3 – 6 months",
                4: "More than 6 months",
            }[x],
        )

        st.divider()

        # ── Section B ────────────────────────────────────────────────────────
        st.markdown("### Section B — Objectives and Time Horizon")

        b1 = st.radio(
            "B1. Primary investment objective",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Preserve capital against inflation",
                2: "Generate stable income",
                3: "Achieve moderate capital growth",
                4: "Maximise long-term capital growth",
            }[x],
        )

        b2 = st.radio(
            "B2. Expected time horizon",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Less than 2 years",
                2: "2 – 5 years",
                3: "5 – 10 years",
                4: "More than 10 years",
            }[x],
        )

        b3 = st.radio(
            "B3. Annual return expectation",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "1% – 3% (capital preservation)",
                2: "3% – 5% (modest growth)",
                3: "5% – 8% (significant growth)",
                4: "Over 8% (aggressive growth)",
            }[x],
        )

        b4 = st.selectbox(
            "B4. Main purpose of the investment (informational only)",
            options=[
                "Retirement supplement",
                "Specific future expense (property, education, project)",
                "Supplementary current income",
                "Long-term growth / inheritance planning",
                "Other",
            ],
        )

        st.divider()

        # ── Section C ────────────────────────────────────────────────────────
        st.markdown("### Section C — Risk Tolerance")
        st.caption("Measures the subjective, psychological and emotional dimension of risk.")

        c1 = st.radio(
            "C1. Your portfolio drops 20% in a few weeks due to market volatility. You would:",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Sell everything to prevent further losses",
                2: "Sell part of the portfolio to reduce risk",
                3: "Hold and wait for recovery",
                4: "Buy more at lower prices",
            }[x],
        )

        c2 = st.radio(
            "C2. Which scenario would you prefer over one year?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Guaranteed return of +2%, no losses",
                2: "Expected +5%, maximum loss –5%",
                3: "Expected +10%, maximum loss –15%",
                4: "Expected +20%, maximum loss –30%",
            }[x],
        )

        c3 = st.radio(
            "C3. At year-end, four portfolios produced these results. Which would you most regret NOT holding?",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Portfolio A: +3%, max drawdown –2%",
                2: "Portfolio B: +6%, max drawdown –8%",
                3: "Portfolio C: +12%, max drawdown –18%",
                4: "Portfolio D: +25%, max drawdown –35%",
            }[x],
        )

        c4 = st.radio(
            "C4. Your general attitude toward uncertainty",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "I avoid it whenever possible",
                2: "I tolerate it cautiously",
                3: "I am comfortable with it",
                4: "I find it stimulating",
            }[x],
        )

        c5 = st.radio(
            "C5. Style of important decisions",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Long, careful analysis",
                2: "Methodical, weighing pros and cons",
                3: "Quick, based on overall judgement",
                4: "Impulsive when opportunity appears",
            }[x],
        )

        c6 = st.radio(
            "C6. Your portfolio underperforms the market for two consecutive years. You feel:",
            options=[1, 2, 3, 4],
            format_func=lambda x: {
                1: "Anxious — I would change strategy immediately",
                2: "Worried — I would reconsider the strategy",
                3: "Patient — I would stick to the long-term plan",
                4: "Unaffected — short-term performance does not worry me",
            }[x],
        )

        st.divider()

        # ── Section D ────────────────────────────────────────────────────────
        st.markdown("### Section D — Knowledge and Experience")
        st.caption(
            "These questions verify your actual financial understanding and act as a filter "
            "on suitable products. Clients with no knowledge cannot be recommended complex "
            "instruments (derivatives, structured products, alternatives)."
        )

        d11 = st.radio(
            "D11. A bond with a duration of 7 years, compared to a bond with a duration of 2 years, is:",
            options=[
                "More sensitive to interest rate changes",
                "Less sensitive",
                "Equally sensitive",
                "I don't know",
            ],
        )

        d12 = st.radio(
            "D12. Diversification primarily reduces:",
            options=[
                "Systematic (market) risk",
                "Specific (idiosyncratic) risk",
                "Both equally",
                "I don't know",
            ],
        )

        d13 = st.radio(
            "D13. An ETF typically differs from an actively managed mutual fund because:",
            options=[
                "It tracks an index and has lower fees",
                "It guarantees higher returns",
                "It cannot be traded intraday",
                "I don't know",
            ],
        )

        d14 = st.radio(
            "D14. 'Leverage' in investing means:",
            options=[
                "Using borrowed money or derivatives to amplify exposure",
                "A type of guaranteed return",
                "A low-risk strategy",
                "I don't know",
            ],
        )

        d15 = st.radio(
            "D15. Past performance of a financial product:",
            options=[
                "Guarantees future returns",
                "Is a useful but not conclusive indicator",
                "Is irrelevant to future returns",
                "I don't know",
            ],
        )

        if st.form_submit_button("Calculate my risk profile", use_container_width=True):
            answers = {
                "section_a": {
                    "a1": a1, "a2": a2, "a3": a3, "a4": a4,
                    "a5": a5, "a6": a6, "a7": a7, "a8": a8,
                },
                "section_b": {"b1": b1, "b2": b2, "b3": b3, "b4": b4},
                "section_c": {
                    "c1": c1, "c2": c2, "c3": c3,
                    "c4": c4, "c5": c5, "c6": c6,
                },
                "section_d": {
                    "d11": d11 == "More sensitive to interest rate changes",
                    "d12": d12 == "Specific (idiosyncratic) risk",
                    "d13": d13 == "It tracks an index and has lower fees",
                    "d14": d14 == "Using borrowed money or derivatives to amplify exposure",
                    "d15": d15 == "Is a useful but not conclusive indicator",
                },
            }
            result = set_risk_profile(token, answers)
            if "risk_score" in result:
                st.session_state.user = get_me(token)
                kl = result.get("knowledge_level", "basic")
                st.success(
                    f"Profile set: **{result['risk_profile']}** "
                    f"(score {result['risk_score']}/68) · Knowledge level: **{kl}**"
                )
                st.rerun()
            else:
                st.error(result.get("detail", "Something went wrong"))

st.divider()

# --- AI advice generation ---
st.subheader("Get Personalized Advice")
st.markdown("The AI analyses your portfolio and risk profile to generate tailored investment advice.")

if not user.get("risk_score"):
    st.info("Complete the risk questionnaire above first.")
else:
    if st.button("Generate AI Advice", use_container_width=True, type="primary"):
        with st.spinner("Thinking... (using Llama 3.3 70B via Groq)"):
            result = get_advice(token)
        if "advice" in result:
            st.markdown("### Advice")
            st.markdown(result["advice"])
        else:
            st.error(result.get("detail", "Could not generate advice"))

    st.divider()
    st.subheader("Previous Advice")
    history = get_advice_history(token)
    if history:
        for item in history:
            with st.expander(f"Generated on {item['created_at'][:10]}"):
                st.markdown(item["content"])
    else:
        st.info("No previous advice yet.")
