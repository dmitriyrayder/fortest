"""Загрузка и валидация данных"""

import pandas as pd
import streamlit as st
from ..config.settings import REQUIRED_COLUMNS


@st.cache_data
def load_and_validate_data(uploaded_file):
    """Загружает и валидирует данные из Excel файла"""
    try:
        progress_bar = st.progress(0)
        progress_bar.progress(25)

        df = pd.read_excel(uploaded_file)
        progress_bar.progress(50)

        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Отсутствуют обязательные колонки: {missing_cols}")
            return None

        progress_bar.progress(75)

        df['Datasales'] = pd.to_datetime(df['Datasales'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Datasales']).sort_values('Datasales')
        df = df[(df['Qty'] >= 0) & (df['Price'] > 0)]

        progress_bar.progress(100)
        progress_bar.empty()

        st.success(f"✅ Данные успешно загружены! Обработано {len(df)} записей")
        return df

    except Exception as e:
        st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
        return None
