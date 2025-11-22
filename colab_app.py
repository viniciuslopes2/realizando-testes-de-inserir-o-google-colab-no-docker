# ==============================================================================
# PASSO 1: Instalando bibliotecas para assegurar que o programa rode.
# ==============================================================================
print("--- [1/7] Bibliotecas serão instaladas via Docker (requirements.txt) ---")
import os
print("Sucesso!")


# ==============================================================================
# PASSO 2: Importando as bibliotecas e configurando pastas.
# ==============================================================================
import subprocess
import time
import atexit
import socket
from flask import Flask, render_template, url_for
import pandas as pd
import re

# Imports para o Mapa
import folium
import json
import geopandas as gpd
from shapely.geometry import mapping
from branca.element import Element
import unicodedata
import difflib

print("\n--- [2/7] Criando a estrutura de pastas do projeto... ---")
os.makedirs("templates", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
print("Pastas 'templates' e 'static/css' prontas.")


# ==============================================================================
# PASSO 3: Carregando os dados diretamente dos CSVs via GitHub (com jsDelivr).
# ==============================================================================
print("\n--- [3/7] Definindo URLs dos arquivos de dados (via jsDelivr CDN)... ---")

urls_csv = {
    "idade_sexo_2022": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/RubyFox%20-%20Dados%20de%202022%20-%20Idade%20e%20sexo.csv",
    "populacao_residencia_2022": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/RubyFox%20-%20Dados%20de%202022%20-%20popula%C3%A7%C3%A3o%20e%20residencia.csv",
    "densidade_demografica_sjc_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/densidade_demografica_sjc_2010.csv",
    "faixa_etaria_homens_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/faixa_etaria_homens_2010.csv",
    "faixa_etaria_mulheres_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/faixa_etaria_mulheres_2010.csv",
    "populacao_residente_sjc_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/populacao_residente_sjc_2010.csv",
    "servicos_publicos_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/servicos_publicos_zonas.csv",
    "frota_veiculos_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/frota_veiculos_sjc.csv",
    "transito_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/transito_zonas_sjc.csv",
    "pop_cresc_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/pop_cresc_zonas_sjc.csv",
    "creches_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/creches_zonas_sjc.csv",
    "escolaridade_por_nivel_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/escolaridade_por_nivel_sjc.csv",
    "ideb_qualidade_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/ideb_qualidade_zonas_sjc.csv",
    "infraestrutura_escolas_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/infraestrutura_escolas_zonas.csv",
    "matriculas_por_periodo_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/matriculas_por_periodo_zonas.csv",
    "alfabetizacao_geral_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/alfabetizacao_geral_sjc.csv",
    "alfabetizacao_por_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/alfabetizacao_por_zonas_sjc.csv",
    "servicos_geriatricos_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/servicos_geriatricos_sjc.csv",
    "unidades_saude_idosos_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/unidades_saude_idosos_zonas.csv",
    "projecao_envelhecimento_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/projecao_envelhecimento_sjc.csv",
    "envelhecimento_por_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/envelhecimento_por_zonas.csv"
}
print("URLs definidas.")


# ==============================================================================
# PASSO 4: Criando o arquivo do dashboard Streamlit
# ==============================================================================
print("\n--- [4/7] Criando o arquivo do dashboard Streamlit (app_dashboard.py)... ---")

# ADICIONADO: Lógica nova dentro do código do Streamlit para filtrar por Zona
streamlit_code = r"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

st.set_page_config(page_title="Dashboard SJC", layout="wide")

@st.cache_data
def carregar_dados_csv(url):
    try:
        df = pd.read_csv(url)
        original_columns = df.columns.tolist()
        rename_map = {}
        for col in original_columns:
            new_col = col.strip().lower()
            replacements = {' ': '_', 'ç': 'c', 'ã': 'a', 'õ': 'o', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u', '+': 'mais', '(': '', ')': ''}
            for old, new in replacements.items():
                new_col = new_col.replace(old, new)
            new_col = re.sub(r'[^a-z0-9_]', '', new_col)
            rename_map[col] = new_col
        df = df.rename(columns=rename_map)
        if 'populacao_residencia_2022' in url and 'densidade' in df.columns:
            df['densidade'] = df['densidade'].astype(str).str.replace(',', '.', regex=False).astype(float)
        return df
    except Exception as e:
        return pd.DataFrame()

urls_csv = {
    "idade_sexo_2022": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/RubyFox%20-%20Dados%20de%202022%20-%20Idade%20e%20sexo.csv",
    "populacao_residencia_2022": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/RubyFox%20-%20Dados%20de%202022%20-%20popula%C3%A7%C3%A3o%20e%20residencia.csv",
    "densidade_demografica_sjc_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/densidade_demografica_sjc_2010.csv",
    "faixa_etaria_homens_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/faixa_etaria_homens_2010.csv",
    "faixa_etaria_mulheres_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/faixa_etaria_mulheres_2010.csv",
    "populacao_residente_sjc_2010": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/populacao_residente_sjc_2010.csv",
    "servicos_publicos_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/servicos_publicos_zonas.csv",
    "frota_veiculos_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/frota_veiculos_sjc.csv",
    "transito_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/transito_zonas_sjc.csv",
    "pop_cresc_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/pop_cresc_zonas_sjc.csv",
    "creches_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/creches_zonas_sjc.csv",
    "escolaridade_por_nivel_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/escolaridade_por_nivel_sjc.csv",
    "ideb_qualidade_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/ideb_qualidade_zonas_sjc.csv",
    "infraestrutura_escolas_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/infraestrutura_escolas_zonas.csv",
    "matriculas_por_periodo_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/matriculas_por_periodo_zonas.csv",
    "alfabetizacao_geral_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/alfabetizacao_geral_sjc.csv",
    "alfabetizacao_por_zonas_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/alfabetizacao_por_zonas_sjc.csv",
    "servicos_geriatricos_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/servicos_geriatricos_sjc.csv",
    "unidades_saude_idosos_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/unidades_saude_idosos_zonas.csv",
    "projecao_envelhecimento_sjc": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/projecao_envelhecimento_sjc.csv",
    "envelhecimento_por_zonas": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/Arquivos%20dados%20CSV/envelhecimento_por_zonas.csv"
}

dataframes = {name: carregar_dados_csv(url) for name, url in urls_csv.items()}

# --- Funções dos gráficos originais (mantidas para uso normal) ---
def normalizar_faixa_etaria_2010(indicador):
    indicador = str(indicador).lower()
    if 'menos de 1' in indicador or '1 a 4' in indicador: return '0 a 4 anos'
    return indicador # Simplificado para o exemplo, usar lógica completa original

def formatar_faixa_display(faixa):
    return faixa.replace('_', ' ').replace(' a ', '-').replace(' anos', '')

def gerar_grafico_sexo(df_idade_sexo_2022, df_faixa_h_2010, df_faixa_m_2010, df_pop_2022, df_pop_res_2010):
    st.header("Análise Populacional")
    st.info("Visualização padrão do gráfico de população por sexo.")
    # (Código original do gráfico de sexo aqui...)

# ... (Outras funções gerar_grafico_* mantidas como no seu código original) ...
# Vou apenas criar a função NOVA para a ZONA abaixo

def gerar_dashboard_exclusivo_zona(zona_selecionada, dataframes):
    st.title(f"📍 Raio-X da Zona {zona_selecionada}")
    st.markdown("---")

    # Filtra os DataFrames pela região
    # Obs: Assume que a coluna se chama 'regiao'
    
    col1, col2 = st.columns(2)
    
    # 1. População e Crescimento
    df_cresc = dataframes["pop_cresc_zonas_sjc"]
    if not df_cresc.empty and 'regiao' in df_cresc.columns:
        dado_zona = df_cresc[df_cresc['regiao'].astype(str).str.contains(zona_selecionada, case=False, na=False)]
        with col1:
            st.subheader("🏙️ População e Crescimento")
            if not dado_zona.empty:
                cresc = dado_zona['crescimento_percentual'].values[0]
                absoluto = dado_zona['crescimento_absoluto'].values[0]
                st.metric(label="Crescimento (2010-2022)", value=f"{cresc}%", delta=f"+{absoluto} pessoas")
            else:
                st.warning("Dados de população não encontrados para esta zona.")

    # 2. Trânsito
    df_transito = dataframes["transito_zonas_sjc"]
    with col2:
        st.subheader("🚗 Trânsito e Mobilidade")
        if not df_transito.empty and 'regiao' in df_transito.columns:
            dado_t = df_transito[df_transito['regiao'].astype(str).str.contains(zona_selecionada, case=False, na=False)]
            if not dado_t.empty:
                cong = dado_t['nivel_congestionamento'].values[0]
                infra = dado_t['infraestrutura_viaria'].values[0]
                st.info(f"**Nível de Congestionamento:** {cong}")
                st.write(f"**Infraestrutura:** {infra}")
                st.write(f"**Problemas:** {dado_t['problemas_principais'].values[0]}")

    st.markdown("---")

    # 3. Educação (Gráfico de Barras específico da zona)
    st.subheader("🎓 Educação: Infraestrutura e Qualidade")
    df_servicos = dataframes["servicos_publicos_zonas"]
    df_ideb = dataframes["ideb_qualidade_zonas_sjc"]
    
    col3, col4 = st.columns(2)
    
    with col3:
        if not df_servicos.empty:
            dado_s = df_servicos[df_servicos['regiao'].astype(str).str.contains(zona_selecionada, case=False, na=False)]
            if not dado_s.empty:
                # Gráfico simples de escolas
                mun = dado_s['escolas_municipais'].values[0]
                est = dado_s['escolas_estaduais'].values[0]
                df_chart = pd.DataFrame({'Tipo': ['Municipais', 'Estaduais'], 'Quantidade': [mun, est]})
                fig = px.bar(df_chart, x='Tipo', y='Quantidade', title=f"Escolas na Zona {zona_selecionada}", color='Tipo')
                st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        if not df_ideb.empty:
            dado_i = df_ideb[df_ideb['regiao'].astype(str).str.contains(zona_selecionada, case=False, na=False)]
            if not dado_i.empty:
                ideb_ini = dado_i['ideb_anos_iniciais_estimado'].values[0]
                ideb_fim = dado_i['ideb_anos_finais_estimado'].values[0]
                st.metric("IDEB (Anos Iniciais)", ideb_ini)
                st.metric("IDEB (Anos Finais)", ideb_fim)
                st.write(f"**Qualidade Infra:** {dado_i['qualidade_infraestrutura'].values[0]}")

    st.markdown("---")
    
    # 4. Idosos e Saúde
    st.subheader("🏥 Saúde e Envelhecimento")
    df_envelhecimento = dataframes["envelhecimento_por_zonas"]
    if not df_envelhecimento.empty:
        dado_e = df_envelhecimento[df_envelhecimento['regiao'].astype(str).str.contains(zona_selecionada, case=False, na=False)]
        if not dado_e.empty:
            perc_idosos = dado_e['percentual_idosos_estimado'].values[0]
            perfil = dado_e['perfil_envelhecimento'].values[0]
            st.progress(int(perc_idosos), text=f"Percentual de Idosos: {perc_idosos}%")
            st.write(f"**Perfil:** {perfil}")
            st.write(f"**Tendência:** {dado_e['tendencia_futura'].values[0]}")

# Lógica Principal do Streamlit
params = st.query_params

# Se tiver parametro ZONA, mostra o dashboard da zona
if "zona" in params:
    zona_url = params.get("zona") # Pode vir como lista dependendo da versão, aqui simplificando
    # Tratamento para pegar string pura se vier em lista
    if isinstance(zona_url, list): zona_url = zona_url[0]
    
    if zona_url:
        gerar_dashboard_exclusivo_zona(zona_url, dataframes)
    else:
        st.error("Zona não especificada.")

# Se não tiver zona, mas tiver grafico_id (comportamento antigo)
elif "grafico_id" in params:
    # ... (Sua lógica existente de chamar gerar_grafico_X fica aqui) ...
    # Para o exemplo não ficar gigante, imagine que suas chamadas if graph_id == 1 etc estão aqui
    st.write("Exibindo gráfico global id: " + str(params.get("grafico_id")))
    
else:
    st.write("Bem-vindo ao Dashboard. Selecione uma opção no site principal.")

"""
STREAMLIT_APP_FILE = "app_dashboard.py"
with open(STREAMLIT_APP_FILE, "w", encoding="utf-8") as f:
    f.write(streamlit_code)
print(f"Arquivo '{STREAMLIT_APP_FILE}' criado com sucesso.")


# ==============================================================================
# PASSO 5: Cria os arquivos do site para o Flask
# ==============================================================================
print("\n--- [5/7] Criando os arquivos HTML e CSS... ---")

# (Mantém layout.html, index.html, grafico.html e style.css iguais ao seu original)
# ... [Código omitido para brevidade, mas você deve rodar o bloco original do PASSO 5] ...

# ADICIONADO: Criando o template novo para a zona
zona_html = """
{% extends "layout.html" %}
{% block content %}
    <main>
        <div class="titulo-container">
            <h1>
                Dados Regionais: {{ nome_zona }}
                <span class="titulo-sublinhado"></span>
            </h1>
        </div>
        <div class="content-container">
            <a href="{{ url_for('home') }}#mapa" style="display:inline-block; margin-bottom:15px; padding: 10px 20px; background-color: #0654A5; color: white; border-radius: 5px;">&larr; Voltar ao Mapa</a>
            
            <div id="loader-container" class="loader-container">
                <div class="loader"></div>
                <p class="loader-text">Carregando dados da {{ nome_zona }}...</p>
            </div>
            
            <!-- Iframe apontando para o Streamlit com o parametro ?zona=Nome -->
            <iframe id="streamlit-iframe" width="100%" height="2000" style="border:none; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); visibility: hidden;"></iframe>
        </div>
    </main>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const iframe = document.getElementById('streamlit-iframe');
            const loader = document.getElementById('loader-container');
            const streamlitUrl = "{{ streamlit_public_url }}";
            const zonaNome = "{{ nome_zona }}";
            
            iframe.onload = function() {
                loader.style.display = 'none';
                iframe.style.visibility = 'visible';
            };
            
            // Monta a URL: http://...:8501/?zona=Sul
            iframe.src = streamlitUrl + "?zona=" + zonaNome;
        });
    </script>
{% endblock %}
"""
with open("templates/zona.html", "w", encoding="utf-8") as f:
    f.write(zona_html)


# ==============================================================================
# PASSO 5.5: Gerando o mapa interativo (Folium) COM O NOVO LINK
# ==============================================================================
print("\n--- [5.5/7] Gerando o mapa interativo... ---")

try:
    url_geojson = 'https://raw.githubusercontent.com/FATCK06/ProjectAPI_FirstSemester/main/Delimita%C3%A7%C3%A3o%20da%20Zona%20de%20SJC/zonas_sjc_poligono.geojson'
    
    # Seus dados originais
    zonas = {
        "Zona Norte": {'populacao': 100000, 'area': 23.35},
        "Zona Sul": {'populacao': 90000, 'area': 32.69},
        "Zona Leste": {'populacao': 120000, 'area': 28.02},
        "Zona Centro": {'populacao': 72401, 'area': 18.68},
        "Zona Oeste": {'populacao': 64482, 'area': 25.66},
        "Zona Sudeste": {'populacao': 62541, 'area': 30.37}
    }
    cores = {"Zona Norte": "#e41a1c", "Zona Sul": "#377eb8", "Zona Leste": "#4daf4a", "Zona Oeste": "#984ea3", "Zona Centro": "#ff7f00", "Zona Sudeste": "#ffff33"}

    gdf = gpd.read_file(url_geojson)
    if gdf.crs is None: gdf.set_crs(epsg=4326, inplace=True)
    gdf_proj = gdf.to_crs(epsg=32723)
    gdf['area_km2'] = gdf_proj.geometry.area / 1e6
    centroids_wgs = gdf_proj.centroid.to_crs(epsg=4326)
    gdf['centroid_lat'] = centroids_wgs.y
    gdf['centroid_lon'] = centroids_wgs.x

    def norm(s):
        if s is None: return ""
        s = str(s)
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
        s = s.lower()
        s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
        return s

    zonas_norm_map = { norm(k): k for k in zonas.keys() }
    
    # Mapeamento para limpar o nome para a URL (Ex: "Zona Sul" -> "Sul")
    # Isso é importante para bater com os nomes nos seus CSVs
    def limpar_nome_para_url(nome_completo):
        return nome_completo.replace("Zona ", "")

    map_center = [gdf['centroid_lat'].mean(), gdf['centroid_lon'].mean()]
    mapa = folium.Map(location=map_center, zoom_start=12, control_scale=True)
    js_functions = []

    for idx, row in gdf.iterrows():
        nome_raw = row.get('nome', '')
        nome_norm = norm(nome_raw)
        possible = difflib.get_close_matches(nome_norm, list(zonas_norm_map.keys()), n=1, cutoff=0.6)
        matched_key = zonas_norm_map[possible[0]] if possible else None

        populacao = zonas[matched_key]['populacao'] if matched_key else None
        area_calc = float(row['area_km2'])
        densidade = (populacao / area_calc) if (populacao and area_calc>0) else None
        cor = cores.get(matched_key if matched_key else nome_raw, "#3388ff")

        # Preparar nome para o link
        nome_limpo = limpar_nome_para_url(matched_key) if matched_key else "Centro"

        lat_c = float(row['centroid_lat'])
        lon_c = float(row['centroid_lon'])
        safe = re.sub(r'\W+', '_', nome_raw if nome_raw else f'zona_{idx}')
        geom_json = json.dumps(mapping(row.geometry))

        js_fn = f"""
        function togglePoly_{safe}(){{
          var map = {mapa.get_name()};
          if(window['poly_{safe}']){{
            map.removeLayer(window['poly_{safe}']);
            window['poly_{safe}'] = null;
          }} else {{
            window['poly_{safe}'] = L.geoJSON({geom_json}, {{
              style: function (feature) {{ return {{color: '{cor}', weight: 2, fillOpacity: 0.45}}; }}
            }}).addTo(map);
            try {{ map.fitBounds(window['poly_{safe}'].getBounds()); }} catch(e){{}}
          }}
        }}
        """
        js_functions.append(js_fn)

        pop_str = f"{int(populacao):,}".replace(',', '.') if populacao else "---"
        area_str = f"{area_calc:.2f}"
        dens_str = f"{densidade:.2f}" if densidade else "---"

        # ATUALIZADO: Popup HTML com o NOVO LINK
        # target="_parent" é essencial para abrir na aba principal, saindo do iframe do mapa
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size:13px; min-width: 180px;">
          <h4 style="margin: 0 0 5px 0;">{matched_key if matched_key else nome_raw}</h4>
          <b>População:</b> {pop_str}<br>
          <b>Área:</b> {area_str} km²<br>
          <b>Densidade:</b> {dens_str}<br>
          <hr style="margin: 5px 0;">
          <a href="#" onclick="togglePoly_{safe}();return false;" style="color: #007bff; text-decoration: none;">👁️ Mostrar/Esconder área</a>
          <br><br>
          <a href="/zona/{nome_limpo}" target="_parent" style="background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; display: block; text-align: center;">📊 Ver Gráficos desta Zona</a>
        </div>
        """

        folium.Marker(
            location=[lat_c, lon_c],
            popup=folium.Popup(popup_html, max_width=330),
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(mapa)

    script_all = "<script>\n" + "\n".join(js_functions) + "\n</script>"
    mapa.get_root().html.add_child(Element(script_all))
    mapa.save("templates/mapa.html")
    print("Mapa interativo atualizado com links salvo em 'templates/mapa.html'.")

except Exception as e:
    print(f"ERRO ao gerar o mapa: {e}")
    with open("templates/mapa.html", "w", encoding="utf-8") as f:
        f.write(f"<html><body><h1>Erro</h1><p>{e}</p></body></html>")


# ==============================================================================
# PASSO 6 e 7: Servidores
# ==============================================================================
# ... (Mantenha o código de inicialização do Streamlit igual) ...

# ATUALIZADO: Flask App com a Nova Rota
app = Flask(__name__)

# Configuração de IP (igual ao original)
AWS_PUBLIC_IP = os.environ.get('AWS_PUBLIC_IP', 'localhost')
STREAMLIT_PORT = 8501
streamlit_public_url = f"http://{AWS_PUBLIC_IP}:{STREAMLIT_PORT}"

# Importando o dicionário de gráficos (necessário redefinir aqui se não estiver no escopo global do script corrido)
graficos_info = {
    1: {"titulo": "População por Sexo", "imagem": "https://cdn.jsdelivr.net/gh/FATCK06/ProjectAPI_FirstSemester@main/.misc/img_template/img_html/img_sex.jpg"},
    # ... (outros itens)
}

@app.route("/")
def home():
    return render_template('index.html', title="Home", graficos=graficos_info)

@app.route("/grafico/<int:grafico_id>")
def pagina_grafico(grafico_id):
    global streamlit_public_url
    grafico = graficos_info.get(grafico_id, {"titulo": "Gráfico"})
    return render_template('grafico.html', title=grafico["titulo"], streamlit_public_url=streamlit_public_url, grafico_id=grafico_id)

@app.route("/mapa")
def pagina_mapa():
    return render_template('mapa.html')

# NOVA ROTA: Captura o clique no link do mapa (/zona/Sul, /zona/Centro, etc)
@app.route("/zona/<nome_zona>")
def pagina_zona(nome_zona):
    global streamlit_public_url
    # Renderiza o novo template passando o nome da zona
    return render_template('zona.html', title=f"Zona {nome_zona}", nome_zona=nome_zona, streamlit_public_url=streamlit_public_url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)