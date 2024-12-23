import json
import typing
import psycopg2

INIT_STATEMENT = """CREATE TABLE IF NOT EXISTS models
(
    id  varchar(64),
    type       varchar(64),
    params     text,
    model_binary    bytea,
    PRIMARY KEY (id)
);"""


class DataBase:
    def __init__(self, dsn: str):
        """Инициализация подключения к базе данных и создание таблицы, если она не существует."""
        self.conn = psycopg2.connect(dsn)
        with self.conn.cursor() as cursor:
            cursor.execute(INIT_STATEMENT)

    def close(self):
        """Закрытие подключения к базе данных."""
        self.conn.close()

    def create_model(self, id_: str, type_: str, params: dict, binary: bytes) -> bool:
        """Создание новой модели в базе данных.

        Args:
            id_ (str): Идентификатор модели.
            type_ (str): Тип модели.
            params (dict): Параметры модели.
            binary (bytes): Бинарные данные модели.

        Returns:
            bool: Успешно ли была создана модель.
        """
        sql = """INSERT INTO models (id, type, params, model_binary) VALUES (%s, %s, %s, %s);"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (id_, type_, json.dumps(params), binary))
            self.conn.commit()
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()
            return False

    def delete_model(self, id_: str):
        """Удаление модели из базы данных по идентификатору.

        Args:
            id_ (str): Идентификатор модели для удаления.
        """
        sql = """DELETE FROM models WHERE id = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (id_,))
            self.conn.commit()

    def get_model(self, id_src: str) -> typing.Optional[dict[str, typing.Any]]:
        """Получение информации о модели по идентификатору.

        Args:
            id_src (str): Идентификатор модели.

        Returns:
            Optional[dict[str, typing.Any]]: Информация о модели или None, если модель не найдена.
        """
        sql = """SELECT id, type, params, model_binary
                 FROM models
                 WHERE id = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (id_src,))
            result = cursor.fetchone()
            if result:
                id_, type_, params, binary = result
                return {
                    "id": id_,
                    "type": type_,
                    "params": json.loads(params),
                    "binary": binary,
                }
        return None

    def get_models(self) -> list[dict]:
        """Получение списка всех моделей в базе данных.

        Returns:
            list[dict]: Список словарей с информацией о моделях.
        """
        sql = """SELECT id, type, params FROM models"""
        result = []
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            for id_, type_, params in cursor.fetchall():
                result.append(
                    {
                        "id": id_,
                        "type": type_,
                        "params": json.loads(params),
                    }
                )
        return result