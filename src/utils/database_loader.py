"""Модуль для подключения к SQL Server базе данных"""

import pandas as pd
import streamlit as st
import time


def load_from_database(db_config):
    """
    Загрузка данных из SQL Server

    Args:
        db_config (dict): Конфигурация подключения к БД
            - host: IP адрес сервера
            - port: Порт (обычно 1433)
            - database: Название базы данных
            - user: Имя пользователя
            - password: Пароль
            - table: Название таблицы

    Returns:
        tuple: (DataFrame, success_flag)
    """
    if not db_config or not all([
        db_config['host'],
        db_config['database'],
        db_config['user'],
        db_config['password']
    ]):
        st.info("👆 Заполните все поля подключения (особенно Server и Password)")
        return None, False

    try:
        df = _fetch_database_data(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            table=db_config['table']
        )

        st.success(f"✅ Загружено {len(df):,} записей из SQL Server")

        # DEBUG: Первые 10 строк для проверки
        with st.expander("🔍 Просмотр загруженных данных из БД", expanded=False):
            st.write("**Первые 10 строк:**")
            st.dataframe(df.head(10), use_container_width=True)
            st.write("**Типы колонок:**")
            st.write(df.dtypes)
            st.write("**Количество NULL значений:**")
            st.write(df.isnull().sum())

        return df, True

    except Exception as e:
        st.error(f"❌ Ошибка подключения к БД: {str(e)}")
        return None, False


@st.cache_data(show_spinner=False)
def _fetch_database_data(host, port, database, user, password, table):
    """
    Кешированная загрузка данных из SQL Server через pymssql

    Args:
        host (str): IP адрес сервера
        port (str): Порт
        database (str): База данных
        user (str): Пользователь
        password (str): Пароль
        table (str): Таблица

    Returns:
        pd.DataFrame: Загруженные данные

    Raises:
        Exception: При ошибках подключения или загрузки
    """
    progress_bar = st.progress(0, text="🔌 Подключение к SQL Server...")
    time.sleep(0.2)

    try:
        import pymssql

        # Подключение через pymssql (без ODBC)
        conn = pymssql.connect(
            server=host,
            port=int(port),
            database=database,
            user=user,
            password=password,
            timeout=15,
            login_timeout=15
        )

        st.success(f"✅ Подключено через pymssql к {host}")

        progress_bar.progress(30, text="📊 Загрузка данных...")

        # SQL запрос
        query = f"""
            SELECT TOP 100000
                shop as Magazin,
                Datasales,
                Art,
                Name_Product as Describe,
                Model,
                Gender as Segment,
                Cost_price as Purchaiseprice,
                Price,
                Qty,
                [Sum]
            FROM [dbo].[{table}]
            WHERE Datasales >= DATEADD(MONTH, -12, GETDATE())
                AND Qty > 0
            ORDER BY Datasales DESC
        """

        df = pd.read_sql(query, conn)
        conn.close()

        progress_bar.progress(90, text="✅ Обработка данных...")
        time.sleep(0.2)

        if len(df) == 100000:
            st.warning("⚠️ Результат обрезан до 100,000 строк")

        progress_bar.progress(100, text="✅ Данные загружены!")
        time.sleep(0.3)
        progress_bar.empty()

        return df

    except ImportError:
        if progress_bar:
            progress_bar.empty()
        raise Exception(
            "Модуль pymssql не установлен. Установите: pip install pymssql"
        )

    except Exception as e:
        if progress_bar:
            progress_bar.empty()

        error_msg = str(e)

        # Обработка различных типов ошибок
        if "Login failed" in error_msg or "18456" in error_msg:
            raise Exception("Ошибка авторизации: неверный логин/пароль")
        elif "Unable to connect" in error_msg or "20009" in error_msg:
            raise Exception(f"Сервер {host} не найден. Проверьте IP и порт.")
        elif "timeout" in error_msg.lower():
            raise Exception("Превышено время ожидания подключения")
        else:
            raise Exception(f"Ошибка SQL Server: {error_msg}")


def validate_database_data(df):
    """
    Валидация данных из базы данных

    Args:
        df (pd.DataFrame): DataFrame для валидации

    Returns:
        pd.DataFrame: Валидированный DataFrame или None
    """
    try:
        from ..config.settings import REQUIRED_COLUMNS

        # Проверка наличия обязательных колонок
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        if missing_cols:
            st.error(f"❌ Отсутствуют обязательные колонки: {missing_cols}")
            st.info(f"Доступные колонки: {list(df.columns)}")
            return None

        # Преобразование типов
        df['Datasales'] = pd.to_datetime(df['Datasales'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['Datasales']).sort_values('Datasales')
        df = df[(df['Qty'] >= 0) & (df['Price'] > 0)]

        return df

    except Exception as e:
        st.error(f"❌ Ошибка при валидации данных: {str(e)}")
        return None


def render_database_connection_ui():
    """
    Отрисовывает UI для настройки подключения к базе данных

    Returns:
        dict: Конфигурация подключения к БД
    """
    st.markdown("### 🔐 Настройка подключения к SQL Server")

    col1, col2 = st.columns(2)

    with col1:
        db_host = st.text_input(
            "Server (IP):",
            value="",
            key="db_host",
            placeholder="Введите IP адрес",
            help="IP адрес SQL Server"
        )
        db_name = st.text_input(
            "Database:",
            value="bdop",
            key="db_name",
            help="Название базы данных"
        )
        db_user = st.text_input(
            "User:",
            value="sales",
            key="db_user",
            help="Имя пользователя"
        )

    with col2:
        db_password = st.text_input(
            "Password:",
            value="",
            type="password",
            key="db_password",
            placeholder="Введите пароль",
            help="Пароль для подключения"
        )
        db_table = st.text_input(
            "Table:",
            value="Sales_table",
            key="db_table",
            help="Название таблицы"
        )
        db_port = st.text_input(
            "Port:",
            value="1433",
            key="db_port",
            help="Порт SQL Server (обычно 1433)"
        )

    db_config = {
        'host': db_host,
        'port': db_port,
        'database': db_name,
        'user': db_user,
        'password': db_password,
        'table': db_table
    }

    return db_config
