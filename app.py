import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="RewardPe B2B", layout="wide", page_icon="🎁")
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def calc_eli(r): return min(100, 0.35*r['purchase_frequency']/12*100 + 0.25*r['engagement_score'] + 0.20*r['sentiment_score'] + 0.20*r['brand_interaction'])
def calc_churn(r): return min(100, max(0, r['last_purchase_days']*0.4 + (100-r['engagement_score'])*0.3 + (100-r['sentiment_score'])*0.3))
def get_seg(e,c): return "Loyal" if e>=70 and c<30 else ("At Risk" if c>=50 else "Dormant")

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(APP_DIR, "data", "sample_customers.csv"))
    df['eli_score'] = df.apply(calc_eli, axis=1)
    df['churn_probability'] = df.apply(calc_churn, axis=1)
    df['segment'] = df.apply(lambda r: get_seg(r['eli_score'], r['churn_probability']), axis=1)
    df['reward'] = df['segment'].map({"Loyal":"VIP Access","At Risk":"Cashback ₹200","Dormant":"Win-back ₹150"})
    df['lift'] = df['segment'].map({"Loyal":"+5%","At Risk":"+25%","Dormant":"+40%"})
    return df

def main():
    if 'step' not in st.session_state: st.session_state.step = 0
    if 'df' not in st.session_state: st.session_state.df = load_data()
    df = st.session_state.df
    
    st.sidebar.title("🎁 RewardPe")
    demo_mode = st.sidebar.checkbox("🎬 DEMO MODE", value=True)
    
    if demo_mode:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Demo Steps")
        steps = ["1️⃣ Upload Data", "2️⃣ AI Segments", "3️⃣ Recommendations", "4️⃣ Dashboard"]
        for i, s in enumerate(steps):
            if i == st.session_state.step: st.sidebar.success(f"▶ {s}")
            elif i < st.session_state.step: st.sidebar.info(f"✅ {s}")
            else: st.sidebar.write(s)
        
        if st.session_state.step == 0:
            st.title("📤 Step 1: Upload Customer Data")
            st.info("Upload your transaction data or use sample data")
            if st.button("📁 Load Sample Data", type="primary"):
                st.session_state.step = 1
                st.rerun()
            st.dataframe(df[['customer_id','name','purchase_frequency','engagement_score','last_purchase_days']].head())
        
        elif st.session_state.step == 1:
            st.title("🤖 Step 2: AI Identifies Customer Segments")
            st.success("✅ Data loaded! AI analyzing...")
            l,a,d = len(df[df['segment']=='Loyal']), len(df[df['segment']=='At Risk']), len(df[df['segment']=='Dormant'])
            c1,c2,c3 = st.columns(3)
            c1.success(f"🌟 Loyal\n\n**{l} customers**")
            c2.warning(f"⚠️ At Risk\n\n**{a} customers**")
            c3.error(f"💤 Dormant\n\n**{d} customers**")
            fig = px.pie(df, names='segment', color='segment', color_discrete_map={'Loyal':'green','At Risk':'orange','Dormant':'red'})
            st.plotly_chart(fig)
            if st.button("Next: See Recommendations →", type="primary"):
                st.session_state.step = 2
                st.rerun()
        
        elif st.session_state.step == 2:
            st.title("🎁 Step 3: AI Reward Recommendations")
            st.markdown("| Segment | Reward | Predicted Lift |")
            st.markdown("|---------|--------|----------------|")
            st.markdown("| 🌟 Loyal | VIP Early Access | +5% |")
            st.markdown("| ⚠️ At Risk | Cashback ₹200 | +25% |")
            st.markdown("| 💤 Dormant | Win-back Bonus ₹150 | +40% |")
            st.subheader("Individual Recommendations")
            st.dataframe(df[['name','segment','eli_score','churn_probability','reward','lift']])
            if st.button("Next: View Dashboard →", type="primary"):
                st.session_state.step = 3
                st.rerun()
        
        elif st.session_state.step == 3:
            st.title("📊 Step 4: Loyalty Health Dashboard")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Health Score", f"{df['eli_score'].mean():.0f}/100", "+5")
            c2.metric("Churn Risk", f"{(df['churn_probability']>50).mean()*100:.0f}%", "-8%")
            c3.metric("Campaign ROI", "4.2x")
            c4.metric("LTV Increase", "+40%")
            
            fig = go.Figure(go.Indicator(mode="gauge+number", value=df['eli_score'].mean(), title={'text':"Loyalty Health"},
                gauge={'axis':{'range':[0,100]},'bar':{'color':"#2E86AB"},'steps':[{'range':[0,40],'color':'red'},{'range':[40,70],'color':'yellow'},{'range':[70,100],'color':'green'}]}))
            st.plotly_chart(fig)
            
            st.success("🎉 Demo Complete! RewardPe can reduce churn by 32% and increase LTV by 40%")
            if st.button("🔄 Restart Demo"):
                st.session_state.step = 0
                st.rerun()
    
    else:
        menu = st.sidebar.selectbox("Menu", ["Dashboard","AI Engine","Campaigns","ROI Calculator"])
        if menu == "Dashboard":
            st.title("📊 Executive Dashboard")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Health", f"{df['eli_score'].mean():.0f}/100")
            c2.metric("Churn Risk", f"{(df['churn_probability']>50).mean()*100:.0f}%")
            c3.metric("ROI", "4.2x")
            c4.metric("Customers", len(df))
            fig = px.pie(df, names='segment')
            st.plotly_chart(fig)
            st.dataframe(df)
        elif menu == "AI Engine":
            st.title("🤖 AI Loyalty Engine")
            st.dataframe(df[['name','segment','eli_score','churn_probability','reward','lift']])
        elif menu == "Campaigns":
            st.title("🎯 Campaign Builder")
            name = st.text_input("Campaign Name")
            seg = st.selectbox("Segment", ["All","Loyal","At Risk","Dormant"])
            if st.button("Launch"): st.success(f"Campaign '{name}' launched!")
        elif menu == "ROI Calculator":
            st.title("💰 ROI Calculator")
            cust = st.number_input("Customers", value=100000)
            churn = st.slider("Churn %", 5, 50, 25)
            saved = int(cust * churn/100 * 0.32)
            st.metric("Customers Saved", f"{saved:,}")
            st.metric("Revenue Protected", f"₹{saved*5000:,}")

if __name__ == "__main__":
    main()
