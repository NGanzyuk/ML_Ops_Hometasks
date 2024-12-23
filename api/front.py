import logging

import requests
import streamlit as st

API_URL = "http://localhost:8000"

logging.basicConfig(level=logging.INFO)

st.title("ML Model Dashboard")


def get_model_list():
    response = requests.get(f"{API_URL}/model_list")
    if response.status_code == 200:
        return response.json()["types"]
    else:
        st.error("Ошибка при получении списка моделей.")
        logging.error("Ошибка при получении списка моделей: %s", response.text)
        return []


def train_model(model_type, params):
    response = requests.post(
        f"{API_URL}/model", json={"model_type": model_type, "params": params}
    )
    if response.status_code == 200:
        st.success("Модель успешно обучена!")
    else:
        st.error("Ошибка при обучении модели.")
        logging.error("Ошибка при обучении модели: %s", response.text)


def get_prediction(model_name, input_data):
    response = requests.get(
        f"{API_URL}/model", params={"model_name": model_name, "input_data": input_data}
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Ошибка при получении предсказания.")
        logging.error("Ошибка при получении предсказания: %s", response.text)
        return None


models = get_model_list()
st.write("Доступные модели: ", models)

with st.form("train_model"):
    model_type = st.selectbox("Выберите модель", models)
    params = st.text_area(
        "Введите параметры модели в формате JSON",
        '{"param1": value1, "param2": value2}',
    )
    submit_button = st.form_submit_button("Обучить модель")
    if submit_button:
        train_model(model_type, params)

with st.form("predict_model"):
    model_name = st.selectbox("Выберите модель для предсказания", models)
    input_data = st.text_area("Введите входные данные для предсказания")
    predict_button = st.form_submit_button("Получить предсказание")
    if predict_button:
        prediction = get_prediction(model_name, input_data)
        if prediction is not None:
            st.write("Предсказание: ", prediction)

with st.form("delete_model"):
    model_to_delete = st.selectbox("Выберите модель для удаления", models)
    delete_button = st.form_submit_button("Удалить модель")
    if delete_button:
        response = requests.delete(
            f"{API_URL}/model", json={"model_name": model_to_delete}
        )
        if response.status_code == 200:
            st.success("Модель успешно удалена!")
        else:
            st.error("Ошибка при удалении модели.")
            logging.error("Ошибка при удалении модели: %s", response.text)
