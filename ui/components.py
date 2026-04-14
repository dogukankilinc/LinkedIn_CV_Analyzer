import streamlit as st

def render_candidate_card(summary: dict):
    st.subheader("👤 Aday Özeti")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Ad Soyad:** {summary.get('name', 'Belirtilmemiş')}")
        st.write(f"**Deneyim:** ~{summary.get('total_experience_years', '?')} Yıl")
        st.write(f"**Güncel Pozisyon:** {summary.get('current_position', '-')}")
        st.write(f"**Şirket:** {summary.get('current_company', '-')}")
    with col2:
        st.write(f"**Eğitim:** {summary.get('education', {}).get('level', '-')} - {summary.get('education', {}).get('field', '-')}")
        st.write(f"**Sektör:** {', '.join(summary.get('sectors', []))}")
        st.write(f"**MATLAB Deneyimi:** {summary.get('matlab_experience', 'Belirsiz')}")
        
    st.write("**Öne Çıkan Beceriler:**")
    skills = summary.get('top_skills', [])
    if skills:
        st.write(" • " + " • ".join(skills))

def render_toolbox_recommendations(rec_data: dict, include_pitch: bool = True):
    toolboxes = rec_data.get("toolboxes", [])
    
    if not toolboxes:
        st.info("Bu kategori için spesifik bir ürün önerisi veya kanıt bulunamadı.")
        return
        
    if include_pitch and rec_data.get("sales_pitch"):
        st.success(f"**💡 Satış Notu:** {rec_data.get('sales_pitch', '')}")
        
    for index, tb in enumerate(toolboxes):
        conf = tb.get('confidence', 'Belirsiz')
        conf_color = "green" if conf == "Yüksek" else "orange" if conf == "Orta" else "red"
        
        st.markdown(f"#### {index + 1}. {tb.get('name', 'Bilinmeyen Toolbox')} &nbsp; `Güven Skoru: {conf}`")
        st.write(f"**Öneri Nedeni:** {tb.get('rationale', '')}")
        st.write(f"**📍 Kaynak Bölüm:** {tb.get('evidence', {}).get('source_section', '')}")
        st.info(f"_{tb.get('evidence', {}).get('original_text', '')}_")
        st.write("—")
