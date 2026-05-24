import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Sayfa yapılandırması
st.set_page_config(
    page_title="İK İstifa Risk Analizi Portalı",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Enjeksiyonu
def inject_custom_css():
    st.markdown(
        """
        <style>
        .main {
            background-color: #F8FAFC;
        }
        .hero-card {
            background: linear-gradient(135deg, #2E86AB 0%, #1F5F7A 100%);
            color: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(46, 134, 171, 0.15);
            margin-bottom: 25px;
        }
        .metric-card {
            background-color: white;
            border: 1px solid #E2E8F0;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
            text-align: center;
        }
        .metric-val {
            font-size: 28px;
            font-weight: bold;
            color: #2E86AB;
        }
        .metric-label {
            font-size: 14px;
            color: #64748B;
            margin-top: 5px;
        }
        .result-safe {
            background-color: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 15px;
            padding: 25px;
            color: #065F46;
        }
        .result-danger {
            background-color: #FEF2F2;
            border: 1px solid #FEE2E2;
            border-radius: 15px;
            padding: 25px;
            color: #991B1B;
        }
        .advice-box {
            background-color: #FFFBEB;
            border-left: 5px solid #F59E0B;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
        }
        h1, h2, h3 {
            color: #1E293B;
            font-family: 'Inter', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

inject_custom_css()

# Proje kök dizinini ve alt yolları dinamik belirleme
base_dir = Path(".")
if not (base_dir / "models").exists() and (base_dir / "final-project").exists():
    base_dir = base_dir / "final-project"

PIPELINE_PATH = base_dir / "models/pipeline.joblib"
MODEL_PATH = base_dir / "models/best_model.joblib"
DATA_PATH = base_dir / "data/raw/veri_seti.csv"
if not DATA_PATH.exists():
    DATA_PATH = Path("veri_seti.csv") # Fallback to workspace root data if final-project/data/raw/veri_seti.csv not present

SUMMARY_PATH = base_dir / "reports/summary.json"
COMPARISON_PATH = base_dir / "reports/model_comparison.csv"

# Caching Data Loading
@st.cache_data
def get_unique_values():
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        return {
            "city_name": sorted(df["city_name"].dropna().unique()),
            "department_name": sorted(df["department_name"].dropna().unique()),
            "job_title": sorted(df["job_title"].dropna().unique()),
            "BUSINESS_UNIT": sorted(df["BUSINESS_UNIT"].dropna().unique()),
            "store_name": sorted(df["store_name"].dropna().unique())
        }
    else:
        # Fallback values if dataset not found
        return {
            "city_name": ["Vancouver", "Terrace", "Kelowna", "Victoria"],
            "department_name": ["Executive", "Store Management", "Meats", "Produce"],
            "job_title": ["CEO", "Store Manager", "Cashier", "Produce Manager"],
            "BUSINESS_UNIT": ["STORES", "HEADOFFICE"],
            "store_name": [35, 18, 16, 37]
        }

@st.cache_resource
def load_ml_assets():
    model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    pipeline = joblib.load(PIPELINE_PATH) if PIPELINE_PATH.exists() else None
    return model, pipeline

unique_vals = get_unique_values()
model, pipeline = load_ml_assets()

# Sidebar Menüsü
st.sidebar.markdown(
    """
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2>📊 İK Karar Destek</h2>
        <p style='color: #64748B;'>Çalışan İstifa Riski Tahmini</p>
    </div>
    """,
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Menü Seçimi",
    [
        "🚀 Yönetici Özeti & Vizyon",
        "👤 Tekil Çalışan Analizi",
        "📂 Toplu İstifa Analizi (CSV)",
        "📊 Model Performans Dashboard",
        "ℹ️ Yardım & Dokümantasyon"
    ]
)

# ----------------------------------------------------
# MENU 1: YÖNETİCİ ÖZETİ
# ----------------------------------------------------
if menu == "🚀 Yönetici Özeti & Vizyon":
    st.markdown(
        """
        <div class="hero-card">
            <h1>Çalışan İstifa (Churn) Tahmin Portalı</h1>
            <p>CRISP-DM Metodolojisiyle Geliştirilen İleri Seviye Makine Öğrenmesi Tabanlı Karar Destek Sistemi</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Rapor özetini yükle
    savings = 1_503_000
    opt_savings = 1_872_000
    opt_threshold = 0.10
    model_name = "Gradient Boosting"
    test_accuracy = "98.7%"
    
    if SUMMARY_PATH.exists():
        with open(SUMMARY_PATH, 'r', encoding='utf-8') as f:
            summary = json.load(f)
            savings = summary.get("net_savings", savings)
            opt_savings = summary.get("optimal_net_savings", opt_savings)
            opt_threshold = summary.get("optimal_threshold", opt_threshold)
            model_name = summary.get("best_model_name", model_name)
            # Find metrics
            for metric in summary.get("metrics", []):
                if metric["Model"] == model_name:
                    test_accuracy = f"{metric['Test Accuracy'] * 100:.1f}%"
                    
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">${opt_savings:,.2f}</div>
                <div class="metric-label">İK Optimum Net Tasarruf</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{opt_threshold:.2f}</div>
                <div class="metric-label">Optimum Karar Eşiği</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{model_name}</div>
                <div class="metric-label">Aktif En Başarılı Model</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-val">{test_accuracy}</div>
                <div class="metric-label">Model Test Doğruluğu</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    st.markdown("### 🎯 Projenin İş Değeri ve Amaç")
    st.write(
        """
        Bir çalışanın istifa edip şirketten ayrılması; işe alım, onboarding süreçleri, zaman kaybı ve departman içi
        kültürel kayıplar dahil olmak üzere ortalama **15,000 USD** ikame maliyeti doğurmaktadır.
        
        Bu sistem, kritik personelin ayrılma olasılığını önceden tahmin ederek İK departmanına erken müdahale şansı tanır. 
        İK departmanı, yüksek riskli personeller için **3,000 USD** bütçeyle elde tutma aksiyonu (prim, terfi, rotasyon) alabilir ve 
        yapılan analizlere göre model destekli kararlar **milyon dolarlık işgücü kayıp maliyetini** önleyebilir.
        """
    )
    
    st.markdown("### 🛠️ CRISP-DM Çerçevesi")
    st.markdown(
        """
        *   **Business Understanding:** İstifa maliyetlerini düşürmek ve en doğru sınıflandırma modelini tespit etmek.
        *   **Data Understanding:** 49k+ panel veri kaydı incelendi, hedef sınıf dengesizliği (%3) ve panel verinin getirdiği sızıntı riskleri saptandı.
        *   **Data Preparation:** Eksik veriler ve hedef sızıntıları temizlendi, OneHot encoding yapıldı ve **çalışan ID bazlı GroupShuffleSplit** ile sızıntısız model verisi hazırlandı.
        *   **Modeling:** 10 farklı model eğitildi.
        *   **Evaluation:** F1-score, Recall, Overfitting ve cross-validation kararlılıkları ile finansal maliyet matrisi üzerinden modeller yarıştı.
        *   **Deployment:** Streamlit portalı yayına alındı.
        """
    )

# ----------------------------------------------------
# MENU 2: TEKİL ANALİZ
# ----------------------------------------------------
elif menu == "👤 Tekil Çalışan Analizi":
    st.markdown("## 👤 Tekil Çalışan İstifa Riski Sorgulama")
    st.write("Aşağıdaki formu doldurarak çalışanın özniteliklerine göre istifa risk skorunu hesaplayabilirsiniz.")
    
    if model is None or pipeline is None:
        st.error("⚠️ Model veya Preprocessing Pipeline dosyaları bulunamadı! Lütfen önce run_modeling.py scriptini çalıştırın.")
    else:
        with st.form("single_prediction_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                age = st.slider("Yaş", min_value=18, max_value=70, value=35)
                length_of_service = st.slider("Hizmet Süresi (Yıl)", min_value=0, max_value=30, value=5)
                gender = st.selectbox("Cinsiyet", ["Female", "Male"])
                
            with col2:
                city = st.selectbox("Şehir", unique_vals["city_name"])
                department = st.selectbox("Departman", unique_vals["department_name"])
                job_title = st.selectbox("Unvan (Job Title)", unique_vals["job_title"])
                
            with col3:
                business_unit = st.selectbox("İş Birimi (Business Unit)", unique_vals["BUSINESS_UNIT"])
                store_name = st.selectbox("Mağaza ID", unique_vals["store_name"])
                status_year = st.number_input("Değerlendirme Yılı", min_value=2006, max_value=2026, value=2015)
                
            submit_btn = st.form_submit_button("Tahmin Et & Risk Analizi Yap")
            
        if submit_btn:
            # Girdi verisi DataFrame oluşturma
            input_data = pd.DataFrame([{
                "age": age,
                "length_of_service": length_of_service,
                "city_name": city,
                "department_name": department,
                "job_title": job_title,
                "store_name": store_name,
                "gender_full": gender,
                "STATUS_YEAR": status_year,
                "BUSINESS_UNIT": business_unit
            }])
            
            # Pipeline ile preprocessing
            processed_input = pipeline.transform(input_data)
            
            # Predict
            pred = model.predict(processed_input)[0]
            
            # Predict Proba
            proba = 0.0
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(processed_input)[0][1]
            
            st.markdown("### 📊 Analiz Sonucu")
            
            if pred == 1:
                st.markdown(
                    f"""
                    <div class="result-danger">
                        <h3>⚠️ YÜKSEK RİSK: Çalışanın İstifa Etme Olasılığı Yüksek!</h3>
                        <p>Model Tahmin Olasılığı: <b>%{proba*100:.2f}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    """
                    <div class="advice-box">
                        <h4>💡 İK Önerilen Elde Tutma Eylemleri:</h4>
                        <ul>
                            <li><b>Birebir Görüşme:</b> Çalışanın motivasyonu, iş tatmini ve tükenmişlik seviyesi değerlendirilmelidir.</li>
                            <li><b>Kariyer Planlaması:</b> Çalışana şirket içi gelişim yolları ve eğitim fırsatları sunulmalıdır.</li>
                            <li><b>Finansal Teşvikler:</b> Piyasa standartları göz önüne alınarak prim veya ücret iyileştirmesi değerlendirilmelidir.</li>
                            <li><b>Esnek Çalışma:</b> İş-yaşam dengesini kurmak üzere çalışma koşulları esnetilebilir.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="result-safe">
                        <h3>✅ DÜŞÜK RİSK: Çalışanın Şirkette Kalma Eğilimi Yüksek.</h3>
                        <p>Model Tahmin Olasılığı (İstifa Riski): <b>%{proba*100:.2f}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ----------------------------------------------------
# MENU 3: TOPLU ANALİZ
# ----------------------------------------------------
elif menu == "📂 Toplu İstifa Analizi (CSV)":
    st.markdown("## 📂 Toplu İstifa Riski Analizi")
    st.write("Çalışan listesini içeren bir CSV dosyası yükleyerek tüm çalışanların istifa riskini aynı anda tahmin edebilirsiniz.")
    
    if model is None or pipeline is None:
        st.error("⚠️ Model veya Preprocessing Pipeline dosyaları bulunamadı! Lütfen önce run_modeling.py scriptini çalıştırın.")
    else:
        uploaded_file = st.file_uploader("Çalışan Veri Kümesi Yükleyin (CSV)", type=["csv"])
        
        if uploaded_file is not None:
            input_df = pd.read_csv(uploaded_file)
            st.write("Yüklenen Veri Önizlemesi (İlk 5 Satır):")
            st.dataframe(input_df.head())
            
            # Kolon kontrolü
            required_cols = ['age', 'length_of_service', 'city_name', 'department_name', 'job_title', 'store_name', 'gender_full', 'STATUS_YEAR', 'BUSINESS_UNIT']
            missing_cols = [c for c in required_cols if c not in input_df.columns]
            
            if missing_cols:
                st.error(f"⚠️ Yüklenen dosyada bazı zorunlu sütunlar eksik: {missing_cols}")
            else:
                if st.button("Toplu Risk Hesapla"):
                    # Preprocessing
                    processed_data = pipeline.transform(input_df[required_cols])
                    
                    # Tahminler
                    preds = model.predict(processed_data)
                    probas = model.predict_proba(processed_data)[:, 1] if hasattr(model, "predict_proba") else preds
                    
                    output_df = input_df.copy()
                    output_df["İstifa Riski Tahmini"] = np.where(preds == 1, "Yüksek Risk", "Düşük Risk")
                    output_df["İstifa Olasılığı (%)"] = (probas * 100).round(2)
                    
                    st.success("Tüm çalışanların tahminleri başarıyla üretildi!")
                    
                    # Risk dağılımı görselleştirmesi
                    risk_counts = pd.Series(preds).value_counts()
                    fig_risk = px.pie(
                        values=risk_counts.values,
                        names=np.where(risk_counts.index == 1, "Yüksek Riskli Çalışanlar", "Düşük Riskli Çalışanlar"),
                        title="Toplu Risk Dağılım Grafiği",
                        color_discrete_sequence=['#A7C7E7', '#F6C6C6']
                    )
                    st.plotly_chart(fig_risk)
                    
                    # Yüksek risklileri listele
                    high_risk_df = output_df[output_df["İstifa Riski Tahmini"] == "Yüksek Risk"].sort_values("İstifa Olasılığı (%)", ascending=False)
                    st.markdown(f"### 🚨 Öncelikli Elde Tutulması Gereken Çalışanlar ({len(high_risk_df)} kişi):")
                    st.dataframe(high_risk_df)
                    
                    # CSV İndirme Butonu
                    csv_data = output_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Tahmin Sonuçlarını İndir (CSV)",
                        data=csv_data,
                        file_name="toplu_istifa_tahminleri.csv",
                        mime="text/csv"
                    )

# ----------------------------------------------------
# MENU 4: MODEL PERFORMANS
# ----------------------------------------------------
elif menu == "📊 Model Performans Dashboard":
    st.markdown("## 📊 Model Performans ve Karşılaştırma Panel")
    
    if not COMPARISON_PATH.exists():
        st.warning("⚠️ Karşılaştırma verileri bulunamadı. Lütfen önce run_modeling.py scriptini çalıştırın.")
    else:
        results_df = pd.read_csv(COMPARISON_PATH)
        
        # Grafik 1: F1-Score Karşılaştırması
        fig_f1 = px.bar(
            results_df.sort_values("F1-Score", ascending=False),
            x="Model", y="F1-Score", color="Recall",
            title="10 Modelin F1-Score ve Recall Başarı Kıyaslaması",
            color_continuous_scale="Purples",
            text="F1-Score"
        )
        fig_f1.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        st.plotly_chart(fig_f1, use_container_width=True)
        
        # Grafik 2: Overfit Analizi (Train Accuracy vs Test Accuracy)
        results_df["Overfit"] = results_df["Train Accuracy"] - results_df["Test Accuracy"]
        fig_overfit = px.bar(
            results_df.sort_values("Overfit", ascending=True),
            x="Model", y="Overfit", color="Overfit",
            title="Modellerin Overfitting Seviyesi (Train vs Test Farkı - Düşük Olan Daha Güvenlidir)",
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_overfit, use_container_width=True)
        
        # Tablo Görünümü
        st.markdown("### Tüm Modellerin Detaylı Performans Tablosu")
        st.dataframe(results_df)
        
        # Kaydedilen görselleri yükleme
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 🎯 Seçilen En İyi Modelin Hata Matrisi (Confusion Matrix)")
            cm_path = base_dir / "figures/confusion_matrix.png"
            if cm_path.exists():
                st.image(str(cm_path), caption="Karmaşıklık Matrisi")
                
            st.markdown("### 🔑 Öznitelik Önem Düzeyleri (Feature Importance)")
            feat_path = base_dir / "figures/feature_importance.png"
            if feat_path.exists():
                st.image(str(feat_path), caption="Top 10 En Önemli Öznitelik")

        with col_right:
            st.markdown("### 📈 Seçilen En İyi Modelin ROC Eğrisi ve AUC Değeri")
            roc_path = base_dir / "figures/roc_curve.png"
            if roc_path.exists():
                st.image(str(roc_path), caption="ROC Eğrisi")
                
            st.markdown("### 📊 Hassasiyet-Duyarlılık (Precision-Recall) Eğrisi")
            pr_path = base_dir / "figures/precision_recall_curve.png"
            if pr_path.exists():
                st.image(str(pr_path), caption="Precision-Recall Eğrisi")

        st.markdown("### 🎯 Karar Eşiği Optimizasyonu (Threshold Tuning)")
        th_path = base_dir / "figures/threshold_tuning.png"
        if th_path.exists():
            st.image(str(th_path), caption="Eşik Olasılığı vs İK Bütçe Tasarrufu ($) - Optimum: 0.10")

        st.markdown("### 📈 İş Analitiği ve İstifa Davranışları")
        col_left_2, col_right_2 = st.columns(2)
        with col_left_2:
            st.markdown("#### 🏢 Departman Bazlı İstifa Oranları")
            dept_path = base_dir / "figures/department_churn.png"
            if dept_path.exists():
                st.image(str(dept_path), caption="Departman Bazlı İstifa Oranları (%)")
                
        with col_right_2:
            st.markdown("#### ⏳ Kıdem Yılına Göre İstifa Oranları")
            service_path = base_dir / "figures/service_length_churn.png"
            if service_path.exists():
                st.image(str(service_path), caption="Kıdem Yılına Göre İstifa Oranları (%)")

        st.markdown("### 🔍 Veri Kalitesi & İkili İlişkiler: Yaş vs Kıdem ve İstifa Durumu")
        biv_path = base_dir / "figures/bivariate_scatter.png"
        if biv_path.exists():
            st.image(str(biv_path), caption="Yaş vs Hizmet Süresi Dağılımı (Kırmızı Noktalar İstifa Edenleri Gösterir)")

# ----------------------------------------------------
# MENU 5: YARDIM & DOKÜMANTASYON
# ----------------------------------------------------
else:
    st.markdown("## ℹ️ Yardım & Kullanım Dokümantasyonu")
    st.markdown(
        """
        ### 💡 Uygulama Nasıl Kullanılır?
        1.  **Yönetici Özeti:** Projenin iş vizyonu, İK departmanına kazandırdığı bütçe tasarrufları ve CRISP-DM süreç detayları bu ekranda bulunur.
        2.  **Tekil Çalışan Analizi:** Belirli bir personelin yaş, kıdem, unvan, departman vb. özelliklerini form üzerinden girerek risk skorunu anında hesaplayabilirsiniz.
        3.  **Toplu İstifa Analizi:** Şirketteki tüm çalışanların toplu özniteliklerini içeren bir CSV yükleyip, istifa risk oranlarıyla birlikte listeyi güncelleyebilirsiniz. Tahmin edilen listeyi tekrar CSV formatında indirebilirsiniz.
        4.  **Model Performans Dashboard:** Hangi algoritmaların (10 farklı model) denendiği, başarı metrikleri (Accuracy, Recall, Precision, F1-Score) ve hata matrisleri bu sayfada detaylandırılır.
        
        ### 📋 CSV Dosya Yükleme Formatı (Kolon İsimleri):
        Toplu analiz yükleme dosyasında aşağıdaki kolonlar bulunmalıdır:
        *   `age`: Çalışanın yaşı (örn. 45)
        *   `length_of_service`: Çalışanın şirketteki kıdem yılı (örn. 12)
        *   `city_name`: Şehir adı (örn. Vancouver)
        *   `department_name`: Departman adı (örn. Meats)
        *   `job_title`: Çalışanın unvanı (örn. Meats Manager)
        *   `store_name`: Mağaza numarası (örn. 35)
        *   `gender_full`: Cinsiyet (Female/Male)
        *   `STATUS_YEAR`: Değerlendirme yapılan yıl (örn. 2015)
        *   `BUSINESS_UNIT`: STORES veya HEADOFFICE
        
        *Not: Modelin eğitimi `veri_seti.csv` üzerindeki panel veri yapısına dayanmaktadır. Sızıntıları engellemek için tüm preprocessing adımları pipeline içinde kapsüllenmiştir.*
        """
    )
