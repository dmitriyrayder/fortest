"""UI компоненты и виджеты"""

import streamlit as st


def show_data_statistics(df):
    """Отображает статистику данных"""
    st.markdown("## 📊 Статистика данных")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""<div class="metric-container">
                <h3>📦 Всего записей</h3>
                <h2>{len(df):,}</h2>
            </div>""",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""<div class="metric-container">
                <h3>🏷️ Уникальных товаров</h3>
                <h2>{df['Art'].nunique():,}</h2>
            </div>""",
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""<div class="metric-container">
                <h3>🏪 Магазинов</h3>
                <h2>{df['Magazin'].nunique()}</h2>
            </div>""",
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""<div class="metric-container">
                <h3>📂 Сегментов</h3>
                <h2>{df['Segment'].nunique()}</h2>
            </div>""",
            unsafe_allow_html=True
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(f"📅 **Период данных**: {df['Datasales'].min().date()} - {df['Datasales'].max().date()}")
    with col2:
        st.info(f"💰 **Общая выручка**: {df['Sum'].sum():.0f} ГРН")
    with col3:
        st.info(f"📈 **Средние продажи/день**: {df.groupby('Datasales')['Qty'].sum().mean():.1f} шт.")


def show_accuracy_table(metrics):
    """Отображает таблицу метрик точности"""
    st.markdown('<div class="accuracy-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Метрики точности модели")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("MAE", f"{metrics['MAE']:.2f}")
    with col2:
        st.metric("RMSE", f"{metrics['RMSE']:.2f}")
    with col3:
        st.metric("MAPE", f"{metrics['MAPE']:.2f}%")
    with col4:
        st.metric("R²", f"{metrics['R2']:.4f}")

    st.markdown('</div>', unsafe_allow_html=True)


def show_forecast_statistics(filtered_df, forecast, forecast_days, magazin, segment):
    """Показывает статистику прогноза"""
    st.markdown("## 📊 Статистика прогноза")

    future_forecast = forecast.tail(forecast_days)
    avg_forecast = future_forecast['yhat'].mean()
    total_forecast = future_forecast['yhat'].sum()

    if len(filtered_df) > 0 and filtered_df['Qty'].sum() > 0:
        avg_price = filtered_df['Sum'].sum() / filtered_df['Qty'].sum()
    else:
        avg_price = 0

    forecast_revenue = total_forecast * avg_price

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📦 Прогноз (средний/день)",
            f"{avg_forecast:.0f} шт."
        )

    with col2:
        st.metric(
            f"📊 Прогноз на {forecast_days} дней",
            f"{total_forecast:.0f} шт."
        )

    with col3:
        st.metric(
            "💰 Прогноз выручки",
            f"{forecast_revenue:.0f} ГРН"
        )


def render_sidebar(df=None):
    """Отрисовывает боковую панель с настройками"""
    with st.sidebar:
        st.markdown("## ⚙️ Настройки")

        uploaded_file = st.file_uploader(
            "📁 Загрузите Excel файл",
            type=['xlsx', 'xls'],
            help="Файл должен содержать колонки: Magazin, Datasales, Art, Describe, Model, Segment, Price, Qty, Sum"
        )

        st.markdown("---")
        st.markdown("### 🔧 Параметры прогноза")

        forecast_days = st.slider(
            "📅 Период прогноза (дней)",
            min_value=7,
            max_value=90,
            value=30,
            step=1
        )

        st.markdown("### 🧹 Предобработка данных")

        remove_outliers = st.checkbox(
            "Удалить выбросы",
            value=True,
            help="Использует метод IQR для удаления аномальных значений"
        )

        smooth_method = st.selectbox(
            "Метод сглаживания",
            options=['none', 'ma', 'ema', 'savgol'],
            format_func=lambda x: {
                'none': 'Без сглаживания',
                'ma': 'Скользящее среднее',
                'ema': 'Экспоненциальное сглаживание',
                'savgol': 'Фильтр Савицкого-Голея'
            }[x]
        )

        if smooth_method != 'none':
            smooth_window = st.slider(
                "Окно сглаживания",
                min_value=3,
                max_value=21,
                value=7,
                step=2
            )
        else:
            smooth_window = 7

    return uploaded_file, forecast_days, remove_outliers, smooth_method, smooth_window


def show_welcome_screen():
    """Экран приветствия при отсутствии данных"""
    st.info("👈 Загрузите Excel файл для начала работы")

    st.markdown("### 📋 Требования к данным")
    st.markdown("""
    Файл должен содержать следующие колонки:
    - **Magazin**: Название магазина
    - **Datasales**: Дата продажи
    - **Art**: Артикул товара
    - **Describe**: Описание товара
    - **Model**: Модель товара
    - **Segment**: Сегмент товара
    - **Price**: Цена
    - **Qty**: Количество
    - **Sum**: Сумма продажи
    """)
