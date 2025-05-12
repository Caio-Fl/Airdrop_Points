import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .titulo {
        font-size:32px;
        font-weight:bold;
        color: #004A87;
        font-family: Arial, sans-serif;
    }
    .subtitulo {
        font-size:24px;
        font-weight:bold;
        color: #004A87;
        border-bottom: 2px solid #0072CE;
        margin-bottom: 10px;
    }
    .valor {
        font-size:48px;
        font-weight:bold;
        color: #004A87;
        margin-top: -10px;
    }
    .parametros {
        font-size:16px;
        line-height: 1.6;
        font-family: Arial, sans-serif;
    }
    .bloco {
        background-color: #f4f8fc;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #d3e3ec;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">Monitor - UHE Simplício</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="bloco">', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">UG-01</div>', unsafe_allow_html=True)
    st.markdown('<div class="valor">62.9 MW</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Parâmetros Elétricos**<br>
    Potência Reativa: 3.6 MVAr<br>
    Corrente de Campo: 443 A<br>
    Corrente Fase A: 2499 A<br>
    Corrente Fase B: 2649 A<br>
    Corrente Fase C: 2693 A</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Gerador**<br>
    Temp. Ar Frio (TE75): 250 °C<br>
    Temp. Fase A (Ranhura 010): 62 °C<br>
    Temp. Fase B (Ranhura 140): 62 °C<br>
    Temp. Fase C (Ranhura 259): 62 °C</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Turbina**<br>
    Abertura Distribuidor: 51.8 %<br>
    Pressão Tampa: -3.8 bar<br>
    Pressão Caixa Espiral: 10.6 bar<br>
    Pressão Tubo Sucção: 0.4 bar</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="bloco">', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">UG-02</div>', unsafe_allow_html=True)
    st.markdown('<div class="valor">0 MW</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Parâmetros Elétricos**<br>
    Potência Reativa: 1.0 MVAr<br>
    Corrente de Campo: -239 A<br>
    Corrente Fase A: 18 A<br>
    Corrente Fase B: 20 A<br>
    Corrente Fase C: -10 A</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Gerador**<br>
    Temp. Ar Frio (TE75): -242 °C<br>
    Temp. Fase A (Ranhura 010): -242 °C<br>
    Temp. Fase B (Ranhura 140): -242 °C<br>
    Temp. Fase C (Ranhura 259): -242 °C</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Turbina**<br>
    Abertura Distribuidor: 0.0 %<br>
    Pressão Tampa: -3.8 bar<br>
    Pressão Caixa Espiral: 10.8 bar<br>
    Pressão Tubo Sucção: 2.0 bar</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="bloco">', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">UG-03</div>', unsafe_allow_html=True)
    st.markdown('<div class="valor">0.2 MW</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Parâmetros Elétricos**<br>
    Potência Reativa: -0.1 MVAr<br>
    Corrente de Campo: -248 A<br>
    Corrente Fase A: 14 A<br>
    Corrente Fase B: -5 A<br>
    Corrente Fase C: 12 A</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Gerador**<br>
    Temp. Ar Frio (TE75): -241.9 °C<br>
    Temp. Fase A (Ranhura 010): -242 °C<br>
    Temp. Fase B (Ranhura 140): -242 °C<br>
    Temp. Fase C (Ranhura 259): -242 °C</div>', unsafe_allow_html=True)
    st.markdown('<div class="parametros">**Turbina**<br>
    Abertura Distribuidor: -0.4 %<br>
    Pressão Tampa: -3.8 bar<br>
    Pressão Caixa Espiral: 10.8 bar<br>
    Pressão Tubo Sucção: 1.1 bar</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)