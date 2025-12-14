"""Вкладка ABC/XYZ анализа"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def calculate_abc_analysis(df, magazin='Все магазины', segment='Все сегменты'):
    """Рассчитывает ABC анализ товаров"""
    filtered = df.copy()

    if magazin != 'Все магазины':
        filtered = filtered[filtered['Magazin'] == magazin]

    if segment != 'Все сегменты':
        filtered = filtered[filtered['Segment'] == segment]

    # Группировка по товарам
    product_sales = filtered.groupby('Model').agg({
        'Sum': 'sum',
        'Qty': 'sum'
    }).reset_index()

    # Сортировка по выручке
    product_sales = product_sales.sort_values('Sum', ascending=False)

    # Расчет накопительной доли
    product_sales['Revenue_Cumsum'] = product_sales['Sum'].cumsum()
    product_sales['Revenue_Percent'] = (product_sales['Sum'] / product_sales['Sum'].sum()) * 100
    product_sales['Revenue_Cumsum_Percent'] = (product_sales['Revenue_Cumsum'] / product_sales['Sum'].sum()) * 100

    # Классификация ABC
    def classify_abc(cumsum_percent):
        if cumsum_percent <= 80:
            return 'A'
        elif cumsum_percent <= 95:
            return 'B'
        else:
            return 'C'

    product_sales['ABC_Class'] = product_sales['Revenue_Cumsum_Percent'].apply(classify_abc)

    return product_sales


def calculate_xyz_analysis(df, magazin='Все магазины', segment='Все сегменты'):
    """Рассчитывает XYZ анализ товаров (по стабильности спроса)"""
    filtered = df.copy()

    if magazin != 'Все магазины':
        filtered = filtered[filtered['Magazin'] == magazin]

    if segment != 'Все сегменты':
        filtered = filtered[filtered['Segment'] == segment]

    # Группировка по товарам и датам
    daily_product_sales = filtered.groupby(['Model', 'Datasales']).agg({
        'Qty': 'sum'
    }).reset_index()

    # Расчет коэффициента вариации для каждого товара
    product_variability = daily_product_sales.groupby('Model').agg({
        'Qty': ['mean', 'std']
    }).reset_index()

    product_variability.columns = ['Model', 'Mean_Qty', 'Std_Qty']

    # Коэффициент вариации
    product_variability['CV'] = np.where(
        product_variability['Mean_Qty'] > 0,
        (product_variability['Std_Qty'] / product_variability['Mean_Qty']) * 100,
        0
    )

    # Классификация XYZ
    def classify_xyz(cv):
        if cv <= 10:
            return 'X'  # Стабильный спрос
        elif cv <= 25:
            return 'Y'  # Переменный спрос
        else:
            return 'Z'  # Нестабильный спрос

    product_variability['XYZ_Class'] = product_variability['CV'].apply(classify_xyz)

    return product_variability


def render_abc_xyz_tab(df, selected_magazin='Все магазины', selected_segment='Все сегменты'):
    """Отрисовывает вкладку ABC/XYZ анализа"""

    st.markdown("## 📊 ABC/XYZ Анализ товаров")

    st.info("""
    **ABC анализ** классифицирует товары по выручке:
    - **A** - 80% выручки (наиболее важные)
    - **B** - следующие 15% выручки
    - **C** - последние 5% выручки

    **XYZ анализ** классифицирует товары по стабильности спроса:
    - **X** - стабильный спрос (CV ≤ 10%)
    - **Y** - переменный спрос (10% < CV ≤ 25%)
    - **Z** - нестабильный спрос (CV > 25%)
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

    # Расчет ABC и XYZ
    abc_data = calculate_abc_analysis(df, selected_magazin, selected_segment)
    xyz_data = calculate_xyz_analysis(df, selected_magazin, selected_segment)

    # Объединение ABC и XYZ
    combined = abc_data.merge(xyz_data[['Model', 'CV', 'XYZ_Class']], on='Model', how='left')
    combined['Combined_Class'] = combined['ABC_Class'] + combined['XYZ_Class']

    # Статистика по классам
    st.markdown("### 📈 Распределение по классам")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ABC Классификация")
        abc_counts = combined['ABC_Class'].value_counts().sort_index()
        abc_revenue = combined.groupby('ABC_Class')['Sum'].sum().sort_index()

        abc_stats = pd.DataFrame({
            'Класс': abc_counts.index,
            'Товаров': abc_counts.values,
            'Выручка': abc_revenue.values,
            '% от общей выручки': (abc_revenue.values / abc_revenue.sum() * 100).round(1)
        })

        st.dataframe(
            abc_stats.style.format({
                'Выручка': '{:.0f} ГРН',
                '% от общей выручки': '{:.1f}%'
            }),
            use_container_width=True
        )

        # График ABC
        fig_abc = go.Figure()
        fig_abc.add_trace(go.Bar(
            x=abc_stats['Класс'],
            y=abc_stats['Товаров'],
            marker_color=['#43e97b', '#feca57', '#ff6b6b'],
            text=abc_stats['Товаров'],
            textposition='outside'
        ))
        fig_abc.update_layout(
            title="Распределение товаров по ABC классам",
            xaxis_title="ABC Класс",
            yaxis_title="Количество товаров",
            height=400
        )
        st.plotly_chart(fig_abc, use_container_width=True)

    with col2:
        st.markdown("#### XYZ Классификация")
        xyz_counts = combined['XYZ_Class'].value_counts().sort_index()
        xyz_revenue = combined.groupby('XYZ_Class')['Sum'].sum().sort_index()

        xyz_stats = pd.DataFrame({
            'Класс': xyz_counts.index,
            'Товаров': xyz_counts.values,
            'Выручка': xyz_revenue.values,
            'Средний CV': combined.groupby('XYZ_Class')['CV'].mean().sort_index().round(1).values
        })

        st.dataframe(
            xyz_stats.style.format({
                'Выручка': '{:.0f} ГРН',
                'Средний CV': '{:.1f}%'
            }),
            use_container_width=True
        )

        # График XYZ
        fig_xyz = go.Figure()
        fig_xyz.add_trace(go.Bar(
            x=xyz_stats['Класс'],
            y=xyz_stats['Товаров'],
            marker_color=['#667eea', '#f093fb', '#feca57'],
            text=xyz_stats['Товаров'],
            textposition='outside'
        ))
        fig_xyz.update_layout(
            title="Распределение товаров по XYZ классам",
            xaxis_title="XYZ Класс",
            yaxis_title="Количество товаров",
            height=400
        )
        st.plotly_chart(fig_xyz, use_container_width=True)

    # Матрица ABC/XYZ
    st.markdown("### 🎯 Матрица ABC/XYZ")

    # Создание сводной таблицы
    matrix_data = combined.groupby(['ABC_Class', 'XYZ_Class']).agg({
        'Model': 'count',
        'Sum': 'sum'
    }).reset_index()

    matrix_pivot = matrix_data.pivot(index='ABC_Class', columns='XYZ_Class', values='Model').fillna(0)

    # Тепловая карта
    fig_matrix = go.Figure(data=go.Heatmap(
        z=matrix_pivot.values,
        x=matrix_pivot.columns,
        y=matrix_pivot.index,
        colorscale='RdYlGn_r',
        text=matrix_pivot.values,
        texttemplate='%{text}',
        textfont={"size": 16},
        hoverongaps=False
    ))

    fig_matrix.update_layout(
        title="Количество товаров в каждой категории ABC/XYZ",
        xaxis_title="XYZ Класс",
        yaxis_title="ABC Класс",
        height=400
    )

    st.plotly_chart(fig_matrix, use_container_width=True)

    # Рекомендации по категориям
    st.markdown("### 💡 Стратегические рекомендации")

    recommendations = {
        'AX': ('🌟 Премиум категория', 'Высокая выручка + стабильный спрос. Обеспечить постоянное наличие, минимизировать риск дефицита.'),
        'AY': ('⚡ Важная категория', 'Высокая выручка + переменный спрос. Мониторинг запасов, гибкое управление.'),
        'AZ': ('⚠️ Проблемная категория', 'Высокая выручка + нестабильный спрос. Детальный анализ причин нестабильности, работа с прогнозами.'),
        'BX': ('✅ Стабильная категория', 'Средняя выручка + стабильный спрос. Автоматизация управления запасами.'),
        'BY': ('🔄 Стандартная категория', 'Средняя выручка + переменный спрос. Регулярный мониторинг.'),
        'BZ': ('📊 Нестабильная категория', 'Средняя выручка + нестабильный спрос. Осторожное управление запасами.'),
        'CX': ('💼 Фоновая категория', 'Низкая выручка + стабильный спрос. Минимальные запасы, возможна оптимизация ассортимента.'),
        'CY': ('📉 Второстепенная категория', 'Низкая выручка + переменный спрос. Рассмотреть целесообразность в ассортименте.'),
        'CZ': ('🗑️ Кандидаты на вывод', 'Низкая выручка + нестабильный спрос. Рассмотреть вывод из ассортимента.')
    }

    col1, col2, col3 = st.columns(3)

    for idx, (cat, (title, desc)) in enumerate(recommendations.items()):
        count = len(combined[combined['Combined_Class'] == cat])
        if count > 0:
            revenue = combined[combined['Combined_Class'] == cat]['Sum'].sum()

            col = [col1, col2, col3][idx % 3]
            with col:
                st.markdown(f"""
                <div class="insight-card">
                    <h4>{cat}: {title}</h4>
                    <p><strong>Товаров:</strong> {count}</p>
                    <p><strong>Выручка:</strong> {revenue:,.0f} ГРН</p>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

    # Детальная таблица
    st.markdown("### 📋 Детальная таблица товаров")

    # Фильтр по классам
    col1, col2 = st.columns(2)

    with col1:
        abc_filter = st.multiselect(
            'Фильтр по ABC классу',
            options=['A', 'B', 'C'],
            default=['A', 'B', 'C']
        )

    with col2:
        xyz_filter = st.multiselect(
            'Фильтр по XYZ классу',
            options=['X', 'Y', 'Z'],
            default=['X', 'Y', 'Z']
        )

    # Применение фильтров
    filtered_combined = combined[
        (combined['ABC_Class'].isin(abc_filter)) &
        (combined['XYZ_Class'].isin(xyz_filter))
    ]

    # Отображение таблицы
    display_table = filtered_combined[['Model', 'ABC_Class', 'XYZ_Class', 'Combined_Class',
                                       'Sum', 'Qty', 'Revenue_Percent', 'CV']].copy()

    display_table.columns = ['Модель', 'ABC', 'XYZ', 'Класс', 'Выручка', 'Количество', '% выручки', 'CV (%)']

    st.dataframe(
        display_table.style.format({
            'Выручка': '{:.0f} ГРН',
            'Количество': '{:.0f}',
            '% выручки': '{:.2f}%',
            'CV (%)': '{:.1f}%'
        }).applymap(
            lambda x: 'background-color: #e8f5e9' if x == 'A' else
                     ('background-color: #fff9c4' if x == 'B' else
                      ('background-color: #ffebee' if x == 'C' else '')),
            subset=['ABC']
        ).applymap(
            lambda x: 'background-color: #e3f2fd' if x == 'X' else
                     ('background-color: #f3e5f5' if x == 'Y' else
                      ('background-color: #fff3e0' if x == 'Z' else '')),
            subset=['XYZ']
        ),
        use_container_width=True,
        height=500
    )

    # Экспорт
    st.markdown("### 📥 Экспорт результатов")

    csv = display_table.to_csv(index=False)
    st.download_button(
        label="📊 Скачать ABC/XYZ анализ (CSV)",
        data=csv,
        file_name=f"abc_xyz_analysis_{selected_magazin}_{selected_segment}.csv",
        mime="text/csv",
        use_container_width=True
    )
