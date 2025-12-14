"""Вкладка анализа ценовой эластичности спроса"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def calculate_price_elasticity(df, magazin='Все магазины', segment='Все сегменты'):
    """Рассчитывает ценовую эластичность спроса для товаров"""

    filtered = df.copy()

    if magazin != 'Все магазины':
        filtered = filtered[filtered['Magazin'] == magazin]

    if segment != 'Все сегменты':
        filtered = filtered[filtered['Segment'] == segment]

    # Получаем уникальные модели
    all_models = filtered['Model'].unique()

    elasticity_data = []

    for model in all_models:
        model_data = filtered[filtered['Model'] == model].copy()

        if len(model_data) >= 10:  # Минимум 10 записей для анализа
            # Группировка по ценовым диапазонам
            try:
                model_data['Price_Group'] = pd.qcut(
                    model_data['Price'],
                    q=3,
                    labels=['Низкая', 'Средняя', 'Высокая'],
                    duplicates='drop'
                )
            except:
                # Если не получается разбить на 3 группы, пробуем на 2
                try:
                    model_data['Price_Group'] = pd.qcut(
                        model_data['Price'],
                        q=2,
                        labels=['Низкая', 'Высокая'],
                        duplicates='drop'
                    )
                except:
                    continue

            price_analysis = model_data.groupby('Price_Group').agg({
                'Price': 'mean',
                'Qty': 'sum'
            }).reset_index()

            if len(price_analysis) >= 2:
                # Простой расчет эластичности между крайними группами
                if price_analysis.iloc[0]['Price'] != price_analysis.iloc[-1]['Price']:
                    price_change_pct = (
                        (price_analysis.iloc[-1]['Price'] - price_analysis.iloc[0]['Price']) /
                        price_analysis.iloc[0]['Price']
                    ) * 100

                    qty_change_pct = (
                        (price_analysis.iloc[-1]['Qty'] - price_analysis.iloc[0]['Qty']) /
                        price_analysis.iloc[0]['Qty']
                    ) * 100

                    if price_change_pct != 0:
                        elasticity = qty_change_pct / price_change_pct

                        # Классификация эластичности
                        if abs(elasticity) > 1:
                            elasticity_type = "Эластичный"
                            recommendation = "Снижение цены увеличит выручку"
                            color = "#ff6b6b"
                        elif abs(elasticity) < 1:
                            elasticity_type = "Неэластичный"
                            recommendation = "Повышение цены увеличит выручку"
                            color = "#51cf66"
                        else:
                            elasticity_type = "Единичный"
                            recommendation = "Цена оптимальна"
                            color = "#ffd43b"

                        total_revenue = model_data['Sum'].sum()
                        avg_price = model_data['Price'].mean()
                        total_qty = model_data['Qty'].sum()

                        elasticity_data.append({
                            'Model': model,
                            'Elasticity': elasticity,
                            'Type': elasticity_type,
                            'Avg_Price': avg_price,
                            'Total_Revenue': total_revenue,
                            'Total_Qty': total_qty,
                            'Price_Change_%': price_change_pct,
                            'Qty_Change_%': qty_change_pct,
                            'Recommendation': recommendation,
                            'Color': color
                        })

    if len(elasticity_data) > 0:
        return pd.DataFrame(elasticity_data).sort_values('Total_Revenue', ascending=False)
    else:
        return None


def render_elasticity_tab(df, selected_magazin='Все магазины', selected_segment='Все сегменты'):
    """Отрисовывает вкладку анализа эластичности"""

    st.markdown("## 💹 Анализ ценовой эластичности спроса")

    st.info("""
    **Ценовая эластичность спроса** показывает, насколько изменяется спрос при изменении цены:

    - **Эластичный спрос (|E| > 1)**: Спрос сильно реагирует на изменение цены
      - При снижении цены на 10%, спрос вырастет более чем на 10%
      - **Стратегия**: Снижение цены увеличит общую выручку

    - **Неэластичный спрос (|E| < 1)**: Спрос слабо реагирует на изменение цены
      - При повышении цены на 10%, спрос упадет менее чем на 10%
      - **Стратегия**: Повышение цены увеличит общую выручку

    - **Единичная эластичность (|E| = 1)**: Изменение спроса пропорционально изменению цены
      - **Стратегия**: Цена близка к оптимальной
    """)

    # Фильтрация данных
    filtered_df = df.copy()

    if selected_magazin != 'Все магазины':
        filtered_df = filtered_df[filtered_df['Magazin'] == selected_magazin]

    if selected_segment != 'Все сегменты':
        filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]

    if len(filtered_df) == 0:
        st.warning("⚠️ Нет данных для выбранных фильтров")
        return

    # Расчет эластичности
    with st.spinner("Расчет ценовой эластичности..."):
        elasticity_df = calculate_price_elasticity(df, selected_magazin, selected_segment)

    if elasticity_df is None or len(elasticity_df) == 0:
        st.warning("⚠️ Недостаточно данных для анализа эластичности. Требуется больше исторических данных с вариацией цен.")
        return

    # Метрики эластичности
    st.markdown("### 📊 Общая статистика")

    col1, col2, col3, col4 = st.columns(4)

    elastic_count = len(elasticity_df[elasticity_df['Type'] == 'Эластичный'])
    inelastic_count = len(elasticity_df[elasticity_df['Type'] == 'Неэластичный'])
    unit_count = len(elasticity_df[elasticity_df['Type'] == 'Единичный'])

    with col1:
        st.metric("📊 Проанализировано товаров", len(elasticity_df))
    with col2:
        st.metric("⚡ Эластичных", elastic_count, help="Чувствительны к цене")
    with col3:
        st.metric("🔒 Неэластичных", inelastic_count, help="Нечувствительны к цене")
    with col4:
        st.metric("⚖️ Единичных", unit_count, help="Оптимальная цена")

    # График эластичности
    st.markdown("### 📈 Распределение коэффициентов эластичности")

    fig_elasticity = go.Figure()

    colors = elasticity_df['Color']

    fig_elasticity.add_trace(go.Bar(
        y=elasticity_df['Model'].head(20),
        x=elasticity_df['Elasticity'].head(20),
        orientation='h',
        marker=dict(
            color=colors.head(20),
            line=dict(color='white', width=1)
        ),
        text=elasticity_df['Elasticity'].head(20).apply(lambda x: f'{x:.2f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Эластичность: %{x:.2f}<extra></extra>'
    ))

    fig_elasticity.add_vline(
        x=-1, line_dash="dash", line_color="red",
        annotation_text="Граница эластичности"
    )
    fig_elasticity.add_vline(x=1, line_dash="dash", line_color="red")

    fig_elasticity.update_layout(
        title="ТОП-20 товаров по коэффициенту эластичности",
        xaxis_title="Коэффициент эластичности",
        yaxis_title="Модель",
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig_elasticity, use_container_width=True)

    # Распределение по типам
    st.markdown("### 🎯 Распределение по типам эластичности")

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart
        type_counts = elasticity_df['Type'].value_counts()

        fig_pie = go.Figure(data=[go.Pie(
            labels=type_counts.index,
            values=type_counts.values,
            marker=dict(colors=['#ff6b6b', '#51cf66', '#ffd43b']),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Товаров: %{value}<br>%{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            title="Распределение товаров по типам эластичности",
            height=400
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Scatter plot: Эластичность vs Выручка
        fig_scatter = go.Figure()

        for etype in elasticity_df['Type'].unique():
            type_data = elasticity_df[elasticity_df['Type'] == etype]

            fig_scatter.add_trace(go.Scatter(
                x=type_data['Elasticity'],
                y=type_data['Total_Revenue'],
                mode='markers',
                name=etype,
                marker=dict(
                    size=10,
                    color=type_data['Color'].iloc[0],
                    line=dict(color='white', width=1)
                ),
                text=type_data['Model'],
                hovertemplate='<b>%{text}</b><br>Эластичность: %{x:.2f}<br>Выручка: %{y:,.0f}<extra></extra>'
            ))

        fig_scatter.update_layout(
            title="Эластичность vs Выручка",
            xaxis_title="Коэффициент эластичности",
            yaxis_title="Выручка (ГРН)",
            height=400,
            hovermode='closest'
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

    # Таблица с рекомендациями
    st.markdown("### 📋 Детальный анализ и рекомендации")

    display_elasticity = elasticity_df.head(30)[
        ['Model', 'Type', 'Elasticity', 'Avg_Price', 'Total_Revenue',
         'Total_Qty', 'Price_Change_%', 'Qty_Change_%', 'Recommendation']
    ].copy()

    display_elasticity = display_elasticity.rename(columns={
        'Model': '🏷️ Модель',
        'Type': '📊 Тип',
        'Elasticity': '📐 Эластичность',
        'Avg_Price': '💰 Средняя цена',
        'Total_Revenue': '💵 Выручка',
        'Total_Qty': '📦 Продано шт.',
        'Price_Change_%': '📈 Изм. цены %',
        'Qty_Change_%': '📊 Изм. объема %',
        'Recommendation': '💡 Рекомендация'
    })

    st.dataframe(
        display_elasticity.style.format({
            '📐 Эластичность': '{:.2f}',
            '💰 Средняя цена': '{:.0f} ГРН',
            '💵 Выручка': '{:.0f} ГРН',
            '📦 Продано шт.': '{:.0f}',
            '📈 Изм. цены %': '{:.1f}%',
            '📊 Изм. объема %': '{:.1f}%'
        }).applymap(
            lambda x: 'background-color: #ffebee' if x == 'Эластичный' else
                     ('background-color: #e8f5e9' if x == 'Неэластичный' else
                      ('background-color: #fff9c4' if x == 'Единичный' else '')),
            subset=['📊 Тип']
        ),
        use_container_width=True,
        height=600
    )

    # Стратегические рекомендации
    st.markdown("### 🎯 Стратегические рекомендации по ценообразованию")

    elastic_revenue = elasticity_df[elasticity_df['Type'] == 'Эластичный']['Total_Revenue'].sum()
    inelastic_revenue = elasticity_df[elasticity_df['Type'] == 'Неэластичный']['Total_Revenue'].sum()
    total_analyzed_revenue = elastic_revenue + inelastic_revenue

    pricing_recommendations = []

    if elastic_count > 0:
        elastic_share = (elastic_revenue / total_analyzed_revenue * 100) if total_analyzed_revenue > 0 else 0
        pricing_recommendations.append(
            f"🔴 **Эластичные товары ({elastic_count} шт., {elastic_share:.1f}% выручки)**: "
            f"Снижение цены на 10-15% может увеличить объем продаж на >10%. "
            f"Используйте акции и промо для роста выручки."
        )

    if inelastic_count > 0:
        inelastic_share = (inelastic_revenue / total_analyzed_revenue * 100) if total_analyzed_revenue > 0 else 0
        pricing_recommendations.append(
            f"🟢 **Неэластичные товары ({inelastic_count} шт., {inelastic_share:.1f}% выручки)**: "
            f"Повышение цены на 5-10% не повлияет критично на спрос. "
            f"Можно увеличить маржинальность."
        )

    if unit_count > 0:
        pricing_recommendations.append(
            f"🟡 **Единично-эластичные товары ({unit_count} шт.)**: "
            f"Цена близка к оптимальной. Сфокусируйтесь на удержании позиций."
        )

    for rec in pricing_recommendations:
        st.markdown(f'<div class="insight-card">{rec}</div>', unsafe_allow_html=True)

    # Общие выводы
    st.info(
        f"💡 **Ключевой вывод**: Из {len(elasticity_df)} проанализированных товаров "
        f"{elastic_count} являются эластичными (чувствительны к цене), "
        f"{inelastic_count} - неэластичными (нечувствительны к цене). "
        f"Используйте эти данные для оптимизации ценовой стратегии."
    )

    # Экспорт
    st.markdown("### 📥 Экспорт результатов")

    csv = display_elasticity.to_csv(index=False)
    st.download_button(
        label="📊 Скачать анализ эластичности (CSV)",
        data=csv,
        file_name=f"elasticity_analysis_{selected_magazin}_{selected_segment}.csv",
        mime="text/csv",
        use_container_width=True
    )
