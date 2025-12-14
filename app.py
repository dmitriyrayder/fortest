"""
Система прогнозирования продаж - Главный файл приложения
Модульная архитектура с вкладками для улучшенного UX
"""

import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Импорты из модулей
from src.config.styles import CSS_STYLES
from src.config.settings import PAGE_CONFIG
from src.utils.file_loader import load_and_validate_data
from src.ui.components import show_data_statistics, render_sidebar, show_welcome_screen
from src.ui.tabs.forecast_tab import render_forecast_tab
from src.ui.tabs.analytics_tab import render_analytics_tab


def main():
    """Главная функция приложения"""

    # Конфигурация страницы
    st.set_page_config(**PAGE_CONFIG)

    # Применение стилей
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    # Заголовок
    st.markdown('<h1 class="main-header">🏪 Система прогнозирования продаж</h1>', unsafe_allow_html=True)

    # Инициализация session_state
    if 'selected_magazin' not in st.session_state:
        st.session_state.selected_magazin = 'Все магазины'
    if 'selected_segment' not in st.session_state:
        st.session_state.selected_segment = 'Все сегменты'

    # Рендер боковой панели
    uploaded_file, forecast_days, remove_outliers, smooth_method, smooth_window = render_sidebar()

    # Проверка наличия загруженного файла
    if uploaded_file is None:
        show_welcome_screen()
        return

    # Загрузка данных
    df = load_and_validate_data(uploaded_file)

    if df is None:
        return

    # Статистика данных
    show_data_statistics(df)

    st.markdown("---")

    # Система вкладок
    tab1, tab2, tab3 = st.tabs([
        "📈 Прогнозирование",
        "📊 Аналитика",
        "📋 Данные"
    ])

    # Вкладка 1: Прогнозирование
    with tab1:
        magazin, segment = render_forecast_tab(
            df,
            st.session_state.selected_magazin,
            st.session_state.selected_segment,
            forecast_days,
            remove_outliers,
            smooth_method,
            smooth_window
        )
        # Обновляем состояние
        st.session_state.selected_magazin = magazin
        st.session_state.selected_segment = segment

    # Вкладка 2: Аналитика
    with tab2:
        render_analytics_tab(
            df,
            st.session_state.selected_magazin,
            st.session_state.selected_segment
        )

    # Вкладка 3: Данные
    with tab3:
        st.markdown("## 📋 Просмотр загруженных данных")

        # Фильтры
        col1, col2 = st.columns(2)

        with col1:
            filter_magazin = st.multiselect(
                "Фильтр по магазинам",
                options=df['Magazin'].unique().tolist(),
                default=[]
            )

        with col2:
            filter_segment = st.multiselect(
                "Фильтр по сегментам",
                options=df['Segment'].unique().tolist(),
                default=[]
            )

        # Применение фильтров
        filtered_data = df.copy()

        if filter_magazin:
            filtered_data = filtered_data[filtered_data['Magazin'].isin(filter_magazin)]

        if filter_segment:
            filtered_data = filtered_data[filtered_data['Segment'].isin(filter_segment)]

        # Отображение данных
        st.dataframe(
            filtered_data,
            use_container_width=True,
            height=500
        )

        # Экспорт данных
        st.markdown("### 📥 Экспорт данных")

        col1, col2, col3 = st.columns(3)

        with col1:
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📊 Скачать CSV",
                data=csv,
                file_name="sales_data.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            st.info(f"📦 Записей: {len(filtered_data):,}")

        with col3:
            st.info(f"💰 Выручка: {filtered_data['Sum'].sum():.0f} ГРН")


if __name__ == "__main__":
    main()
