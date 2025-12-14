"""Вкладка прогнозирования"""

import streamlit as st
from ...models.prophet_model import train_prophet_model, calculate_model_accuracy
from ...utils.data_processing import prepare_prophet_data
from ...visualization.plots import plot_data_preprocessing, plot_forecast, plot_prophet_components
from ..components import show_accuracy_table, show_forecast_statistics


def render_forecast_tab(df, selected_magazin, selected_segment, forecast_days,
                        remove_outliers, smooth_method, smooth_window):
    """Отрисовывает вкладку прогнозирования"""

    st.markdown("## 🎯 Выбор параметров анализа")

    col1, col2 = st.columns(2)

    with col1:
        available_magazins = ['Все магазины'] + sorted(df['Magazin'].unique().tolist())
        magazin = st.selectbox("🏪 Выберите магазин", available_magazins,
                              index=available_magazins.index(selected_magazin) if selected_magazin in available_magazins else 0)

    with col2:
        if magazin == 'Все магазины':
            available_segments = ['Все сегменты'] + sorted(df['Segment'].unique().tolist())
        else:
            magazin_df = df[df['Magazin'] == magazin]
            available_segments = ['Все сегменты'] + sorted(magazin_df['Segment'].unique().tolist())

        segment = st.selectbox("📂 Выберите сегмент", available_segments,
                              index=available_segments.index(selected_segment) if selected_segment in available_segments else 0)

    if st.button("🚀 Создать прогноз", type="primary", use_container_width=True):
        with st.spinner("🔄 Обучение модели..."):
            filtered_df = df.copy()

            if magazin != 'Все магазины':
                filtered_df = filtered_df[filtered_df['Magazin'] == magazin]

            if segment != 'Все сегменты':
                filtered_df = filtered_df[filtered_df['Segment'] == segment]

            if len(filtered_df) < 10:
                st.error("❌ Недостаточно данных для прогнозирования (минимум 10 записей)")
                return magazin, segment

            prophet_data, original_data = prepare_prophet_data(
                filtered_df,
                remove_outliers=remove_outliers,
                smooth_method=smooth_method if smooth_method != 'none' else None,
                smooth_window=smooth_window
            )

            # Предобработка данных
            if remove_outliers or (smooth_method and smooth_method != 'none'):
                st.markdown("## 🧹 Предварительная обработка данных")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 📊 Статистика до обработки")
                    st.metric("Среднее", f"{original_data['y'].mean():.2f}")
                    st.metric("Std. отклонение", f"{original_data['y'].std():.2f}")
                    volatility_before = (original_data['y'].std()/original_data['y'].mean()*100) if original_data['y'].mean() > 0 else 0
                    st.metric("Волатильность", f"{volatility_before:.1f}%")

                with col2:
                    st.markdown("### ✨ Статистика после обработки")
                    st.metric("Среднее", f"{prophet_data['y'].mean():.2f}",
                             delta=f"{prophet_data['y'].mean() - original_data['y'].mean():.2f}")
                    st.metric("Std. отклонение", f"{prophet_data['y'].std():.2f}",
                             delta=f"{prophet_data['y'].std() - original_data['y'].std():.2f}")
                    volatility_after = (prophet_data['y'].std()/prophet_data['y'].mean()*100) if prophet_data['y'].mean() > 0 else 0
                    st.metric("Волатильность", f"{volatility_after:.1f}%",
                             delta=f"{volatility_after - volatility_before:.1f}%")

                fig_preprocessing = plot_data_preprocessing(
                    original_data, prophet_data,
                    "🔄 Сравнение: Оригинальные vs Обработанные данные"
                )
                st.plotly_chart(fig_preprocessing, use_container_width=True, key="preprocessing")

            # Обучение модели
            model, forecast = train_prophet_model(prophet_data, periods=forecast_days)

            if model is None or forecast is None:
                return magazin, segment

            st.success("✅ Модель успешно обучена!")

            # Метрики точности
            accuracy_metrics = calculate_model_accuracy(prophet_data, model)
            if accuracy_metrics:
                show_accuracy_table(accuracy_metrics)

            # Статистика прогноза
            show_forecast_statistics(filtered_df, forecast, forecast_days, magazin, segment)

            # График прогноза
            st.markdown("## 📈 Прогноз продаж")
            fig_main = plot_forecast(
                prophet_data,
                forecast,
                f"Прогноз продаж - {magazin} / {segment}"
            )
            st.plotly_chart(fig_main, use_container_width=True, key="main_forecast")

            # Компоненты модели
            st.markdown("## 🔍 Детальный анализ")
            fig_components = plot_prophet_components(model, forecast)
            st.plotly_chart(fig_components, use_container_width=True, key="prophet_components")

            # Сохраняем результаты в session_state для использования в других вкладках
            st.session_state['last_forecast'] = {
                'model': model,
                'forecast': forecast,
                'prophet_data': prophet_data,
                'filtered_df': filtered_df,
                'magazin': magazin,
                'segment': segment,
                'accuracy_metrics': accuracy_metrics
            }

    return magazin, segment
