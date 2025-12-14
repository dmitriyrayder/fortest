"""Вкладка аналитики"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ...config.settings import WEEKDAY_TRANSLATION


def render_analytics_tab(df, selected_magazin='Все магазины', selected_segment='Все сегменты'):
    """Отрисовывает вкладку аналитики"""

    st.markdown("## 📊 Расширенная аналитика продаж")

    # Фильтрация данных
    filtered_df = df.copy()

    if selected_magazin != 'Все магазины':
        filtered_df = filtered_df[filtered_df['Magazin'] == selected_magazin]

    if selected_segment != 'Все сегменты':
        filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]

    if len(filtered_df) == 0:
        st.warning("⚠️ Нет данных для выбранных фильтров")
        return

    # Анализ по дням недели
    st.markdown("### 📅 Анализ продаж по дням недели")

    filtered_df_weekday = filtered_df.copy()
    filtered_df_weekday['Weekday'] = filtered_df_weekday['Datasales'].dt.dayofweek
    filtered_df_weekday['Weekday_Name'] = filtered_df_weekday['Datasales'].dt.day_name()
    filtered_df_weekday['Weekday_Name_RU'] = filtered_df_weekday['Weekday_Name'].map(WEEKDAY_TRANSLATION)

    weekday_stats = filtered_df_weekday.groupby(['Weekday', 'Weekday_Name_RU']).agg({
        'Qty': 'sum',
        'Sum': 'sum'
    }).reset_index().sort_values('Weekday')

    col1, col2 = st.columns(2)

    with col1:
        fig_weekday_qty = go.Figure()
        fig_weekday_qty.add_trace(go.Bar(
            x=weekday_stats['Weekday_Name_RU'],
            y=weekday_stats['Qty'],
            marker_color='#667eea',
            text=weekday_stats['Qty'].apply(lambda x: f'{x:.0f}'),
            textposition='outside'
        ))
        fig_weekday_qty.update_layout(
            title="Объем продаж по дням недели",
            xaxis_title="День недели",
            yaxis_title="Количество",
            height=400
        )
        st.plotly_chart(fig_weekday_qty, use_container_width=True)

    with col2:
        fig_weekday_revenue = go.Figure()
        fig_weekday_revenue.add_trace(go.Bar(
            x=weekday_stats['Weekday_Name_RU'],
            y=weekday_stats['Sum'],
            marker_color='#f5576c',
            text=weekday_stats['Sum'].apply(lambda x: f'{x:.0f}'),
            textposition='outside'
        ))
        fig_weekday_revenue.update_layout(
            title="Выручка по дням недели",
            xaxis_title="День недели",
            yaxis_title="Выручка (ГРН)",
            height=400
        )
        st.plotly_chart(fig_weekday_revenue, use_container_width=True)

    # Топ товаров
    st.markdown("### 🏆 Топ товаров по продажам")

    top_products = filtered_df.groupby('Model').agg({
        'Qty': 'sum',
        'Sum': 'sum'
    }).reset_index().sort_values('Sum', ascending=False).head(10)

    col1, col2 = st.columns(2)

    with col1:
        fig_top_products = go.Figure()
        fig_top_products.add_trace(go.Bar(
            y=top_products['Model'],
            x=top_products['Sum'],
            orientation='h',
            marker_color='#43e97b',
            text=top_products['Sum'].apply(lambda x: f'{x:.0f} ГРН'),
            textposition='outside'
        ))
        fig_top_products.update_layout(
            title="ТОП-10 товаров по выручке",
            xaxis_title="Выручка (ГРН)",
            yaxis_title="Модель",
            height=500
        )
        st.plotly_chart(fig_top_products, use_container_width=True)

    with col2:
        st.markdown("#### 📋 Детальная информация")
        display_top = top_products[['Model', 'Qty', 'Sum']].copy()
        display_top.columns = ['Модель', 'Количество', 'Выручка']
        st.dataframe(
            display_top.style.format({
                'Количество': '{:.0f}',
                'Выручка': '{:.0f} ГРН'
            }),
            use_container_width=True,
            height=500
        )

    # Анализ по месяцам
    st.markdown("### 📆 Анализ по месяцам")

    filtered_df_monthly = filtered_df.copy()
    filtered_df_monthly['Month'] = filtered_df_monthly['Datasales'].dt.to_period('M')

    monthly_stats = filtered_df_monthly.groupby('Month').agg({
        'Qty': 'sum',
        'Sum': 'sum',
        'Art': 'nunique'
    }).reset_index()

    monthly_stats['Month'] = monthly_stats['Month'].dt.to_timestamp()

    fig_monthly = go.Figure()

    fig_monthly.add_trace(go.Bar(
        x=monthly_stats['Month'],
        y=monthly_stats['Qty'],
        name='Количество',
        marker_color='#667eea'
    ))

    fig_monthly.add_trace(go.Scatter(
        x=monthly_stats['Month'],
        y=monthly_stats['Sum'],
        name='Выручка',
        yaxis='y2',
        line=dict(color='#f5576c', width=3)
    ))

    fig_monthly.update_layout(
        title="Динамика продаж и выручки по месяцам",
        xaxis_title="Месяц",
        yaxis_title="Количество",
        yaxis2=dict(
            title="Выручка (ГРН)",
            overlaying='y',
            side='right'
        ),
        height=500,
        hovermode='x unified'
    )

    st.plotly_chart(fig_monthly, use_container_width=True)
