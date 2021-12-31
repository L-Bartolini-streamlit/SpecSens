import streamlit as st 
import requests
from PIL import Image 
import plotly.graph_objects as go

st.title("Specificity and Sensitivity")

def updateSpecSens():
    if "Roche" in st.session_state.testType:
        if "Symptomatic" in st.session_state.testType:
            st.session_state.sens = 65.3
            st.session_state.spec = 99.9
        if "Asymptomatic" in st.session_state.testType:
            st.session_state.sens = 44.0
            st.session_state.spec = 99.9
    if "Coris" in st.session_state.testType:
        st.session_state.sens = 34.1
    if "ID" in st.session_state.testType:
        st.session_state.sens = 73.0
        st.session_state.spec = 99.7
    if "Xpert Xpress" in st.session_state.testType:
        st.session_state.sens = 100
        st.session_state.spec = 97.2    

#TODO logarithmic slider? 
test = st.sidebar.radio(
    "Select test type: ",
    ["(Symptomatic) Roche/SD Biosensor rapid antigen",
     "(Asymptomatic) Roche/SD Biosensor rapid antigen",
     "(Symptomatic) Coris BIOCONCEPT",
     "(Symptomatic) ID NOW",
     "(Symptomatic) Xpert Xpress"
     ],
    on_change=updateSpecSens,
    key="testType"
)

# ROCHE -> https://pubmed.ncbi.nlm.nih.gov/34242764/
# 

spec = st.sidebar.slider("Specificity (%)", key="spec", min_value=50., max_value=100.,value=90., step = 0.1)
sens = st.sidebar.slider("Sensitivity (%)", key="sens", min_value=50., max_value=100.,value=90., step = 0.1)
# PPV =  st.sidebar.slider("PPV", key="PPV", min_value=0., max_value=100., step = 0.1)
# NPV =  st.sidebar.slider("NPV", key="PPV", min_value=0., max_value=100., step = 0.1)
prevalence = st.sidebar.slider("Prevalence (%)", key="prevalence", min_value=0.5, max_value=100., value=14.2, step = 0.1)

spec = spec/100
sens = sens/100
prevalence = prevalence/100

# N_tot is the N of population 
width, height = 1024, 768
N_tot = width*height

# number true negative
TN = ( N_tot * (1-prevalence) ) / (1 + (spec**-1 - 1))
TN = round(TN)
# number false positives
FP = TN * (spec**-1 - 1)
FP = round(FP)
# number true positive
TP = ( N_tot * prevalence ) / (1 + (sens**-1 - 1))
TP = round(TP)
# number false negatives
FN = TP * (sens**-1 - 1)
FN = round(FN)

with st.expander("Explanation:"):
    url = r"https://www.frontiersin.org/files/Articles/308890/fpubh-05-00307-HTML/image_m/fpubh-05-00307-g001.jpg"
    url = r"https://upload.medbullets.com/topic/101006/images/sensitivity-specificity_corrected.jpg"
    st.image(Image.open(requests.get(url, stream=True).raw))
    st.write(f"[Testing and Screening]({url})")


diseased_width = round(prevalence * width)
healthy_width = width - diseased_width

h_TP = round(TP/diseased_width)
h_FN = height - h_TP
h_FP = round(FP/healthy_width)
h_TN = height - h_FP

fig = go.Figure()

rectangles = {
    'True Positive' : ['red', [0, diseased_width, diseased_width, 0], [0, 0, -h_TP, -h_TP]],
    'False Negative' : ['darkorange', [0, diseased_width, diseased_width, 0], [-h_TP, -h_TP, -height, -height]],
    'False Positive' : ['mediumblue', [diseased_width, width, width, diseased_width], [0, 0, -h_FP, -h_FP]],
    'True Negative' : ['forestgreen', [diseased_width, width, width, diseased_width],[-h_FP, -h_FP, -height, -height]]
}
explanations = {
    'True Positive' : '',
    'False Negative' : '',
    'False Positive' : '',
    'True Negative' : ''
}

for label, properties in rectangles.items():
    fig.add_trace(go.Scatter(
        x=properties[1],
        y=properties[2],
        name = label,
        hovertemplate = '<extra></extra>',
        showlegend=False,
        line = dict(
            color = 'black',
            width = 1.5
        ),
        fillcolor = properties[0],
        fill="toself",
        mode="lines",
    ))


fig.update_xaxes(
    range=[0, width], 
    showgrid=False,
    showticklabels=False,
    zeroline=False,)

fig.update_yaxes(
    range=[-height, 0], showgrid=False,
    showticklabels=False,
    zeroline=False,)

fig.update_layout(
    showlegend=False,
    hoverlabel=dict(
        bgcolor="white",
        font_size=16,)
    )

st.plotly_chart(fig)
