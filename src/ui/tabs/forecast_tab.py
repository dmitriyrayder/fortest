"""Вкладка прогнозирования"""

import streamlit as st
import pandas as pd
from ...models.prophet_model import train_prophet_model, calculate_model_accuracy
from ...utils.data_processing import prepare_prophet_data
from ...visualization.plots import (
    plot_data_preprocessing, plot_forecast, plot_prophet_components,
    plot_sales_by_weekday, plot_top_products, plot_monthly_revenue_trend,
    plot_sales_heatmap, plot_daily_sales_distribution, plot_sales_trend_comparison
)
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

            # Расширенная аналитика продаж
            st.markdown("---")
            st.markdown("## 📊 Расширенная аналитика продаж")

            # Анализ продаж по дням недели
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['weekday'] = pd.to_datetime(filtered_df_copy['Datasales']).dt.day_name()
            filtered_df_copy['date'] = pd.to_datetime(filtered_df_copy['Datasales']).dt.date

            # Агрегация по дням недели для статистики
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

            weekday_stats = filtered_df_copy.groupby('weekday').agg({
                'Sum': 'sum',
                'Qty': 'sum'
            }).reindex(weekday_order)

            best_day_idx = weekday_stats['Sum'].idxmax()
            worst_day_idx = weekday_stats['Sum'].idxmin()
            best_day_name = weekday_ru[weekday_order.index(best_day_idx)]
            worst_day_name = weekday_ru[weekday_order.index(worst_day_idx)]

            # Топ товары
            top_products = filtered_df.groupby('Art').agg({
                'Describe': 'first',
                'Sum': 'sum',
                'Qty': 'sum',
                'Price': 'mean'
            }).sort_values('Sum', ascending=False).head(10)

            # Месячная динамика
            filtered_df_copy['month'] = pd.to_datetime(filtered_df_copy['Datasales']).dt.to_period('M')
            monthly_data = filtered_df_copy.groupby('month')['Sum'].sum()

            # Расчет тренда роста
            if len(monthly_data) >= 2:
                import numpy as np
                trend_pct = ((monthly_data.iloc[-1] - monthly_data.iloc[0]) / monthly_data.iloc[0] * 100) if monthly_data.iloc[0] > 0 else 0
            else:
                trend_pct = 0

            # Статистика в карточках
            st.markdown("### 📈 Ключевые показатели")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "🏆 Лучший день недели",
                    best_day_name,
                    f"{weekday_stats.loc[best_day_idx, 'Sum']:.0f} ГРН"
                )

            with col2:
                st.metric(
                    "⚠️ Худший день недели",
                    worst_day_name,
                    f"{weekday_stats.loc[worst_day_idx, 'Sum']:.0f} ГРН"
                )

            with col3:
                st.metric(
                    "🎯 ТОП товар",
                    top_products.index[0] if len(top_products) > 0 else "N/A",
                    f"{top_products.iloc[0]['Sum']:.0f} ГРН" if len(top_products) > 0 else "0 ГРН"
                )

            with col4:
                st.metric(
                    "📊 Тренд",
                    "Рост" if trend_pct > 0 else "Падение",
                    f"{abs(trend_pct):.1f}%"
                )

            # Графики
            st.markdown("### 📅 Анализ продаж по дням недели")

            col1, col2 = st.columns(2)

            with col1:
                fig_weekday = plot_sales_by_weekday(filtered_df)
                st.plotly_chart(fig_weekday, use_container_width=True, key="sales_weekday")

            with col2:
                fig_distribution = plot_daily_sales_distribution(filtered_df)
                st.plotly_chart(fig_distribution, use_container_width=True, key="daily_distribution")

            # Тепловая карта
            if len(filtered_df_copy['month'].unique()) > 1:
                st.markdown("### 🔥 Тепловая карта продаж")
                fig_heatmap = plot_sales_heatmap(filtered_df)
                st.plotly_chart(fig_heatmap, use_container_width=True, key="sales_heatmap")

            # Топ товары и месячная динамика
            st.markdown("### 🏆 Топ товары и динамика выручки")

            col1, col2 = st.columns(2)

            with col1:
                fig_top_products = plot_top_products(filtered_df, top_n=10)
                st.plotly_chart(fig_top_products, use_container_width=True, key="top_products")

            with col2:
                fig_monthly = plot_monthly_revenue_trend(filtered_df)
                st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_revenue")

            # Сравнение периодов
            if len(filtered_df_copy['date'].unique()) >= 14:
                st.markdown("### 📊 Сравнение периодов")
                fig_comparison = plot_sales_trend_comparison(filtered_df)
                st.plotly_chart(fig_comparison, use_container_width=True, key="period_comparison")

            # Детальная таблица топ товаров
            st.markdown("### 📋 Детальная информация: ТОП-10 товаров")

            # Форматируем таблицу
            top_products_display = top_products.reset_index()
            top_products_display.columns = ['Артикул', 'Описание', 'Выручка', 'Количество', 'Средняя цена']
            top_products_display['Выручка'] = top_products_display['Выручка'].round(2)
            top_products_display['Средняя цена'] = top_products_display['Средняя цена'].round(2)
            top_products_display['Доля в выручке %'] = (
                top_products_display['Выручка'] / filtered_df['Sum'].sum() * 100
            ).round(2)

            st.dataframe(
                top_products_display,
                use_container_width=True,
                height=400,
                hide_index=True
            )

            # Дополнительная аналитика
            st.markdown("### 💡 Инсайты")

            col1, col2 = st.columns(2)

            with col1:
                st.info(f"""
                **📊 Анализ дней недели:**
                - Лучший день: **{best_day_name}** ({weekday_stats.loc[best_day_idx, 'Sum']:.0f} ГРН)
                - Худший день: **{worst_day_name}** ({weekday_stats.loc[worst_day_idx, 'Sum']:.0f} ГРН)
                - Разница: **{(weekday_stats.loc[best_day_idx, 'Sum'] - weekday_stats.loc[worst_day_idx, 'Sum']):.0f} ГРН**
                - Рекомендация: Усилить маркетинг в {worst_day_name.lower()}
                """)

            with col2:
                top_10_revenue = top_products['Sum'].sum()
                total_revenue = filtered_df['Sum'].sum()
                top_10_share = (top_10_revenue / total_revenue * 100) if total_revenue > 0 else 0

                st.success(f"""
                **🎯 Анализ товаров:**
                - ТОП-10 товаров: **{top_10_share:.1f}%** от выручки
                - Всего товаров: **{filtered_df['Art'].nunique()}** шт.
                - Средний чек: **{filtered_df['Price'].mean():.2f} ГРН**
                - Концентрация: {'Высокая' if top_10_share > 50 else 'Средняя' if top_10_share > 30 else 'Низкая'}
                """)

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
