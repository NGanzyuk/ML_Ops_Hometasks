import logging
import time
from concurrent import futures

import grpc
import pandas as pd

import model_service_pb2
import model_service_pb2_grpc
from models.model_factory import modelTypes

logging.basicConfig(level=logging.INFO)


class ModelService(model_service_pb2_grpc.ModelServiceServicer):
    def __init__(self):
        self.models = {}

    def GetModelList(self, request, context):
        logging.info("Получение списка моделей.")
        return model_service_pb2.ModelList(types=list(modelTypes.keys()))

    def TrainModel(self, request, context):
        logging.info(f"Обучение модели: {request.model_type} с параметрами: {request.params}")

        model_class = modelTypes.get(request.model_type)
        if model_class is None:
            context.set_details(f"Модель типа '{request.model_type}' не найдена.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return model_service_pb2.TrainResponse(status="failed")

        params = {k: v for k, v in request.params.fields.items()}
        model = model_class(params=params)

        x_train = pd.DataFrame([[1, 2], [3, 4], [5, 6]])
        y_train = [0, 1, 0]

        model.fit(x_train, y_train)

        model_name = f"{request.model_type}_{len(self.models)}"
        self.models[model_name] = model
        return model_service_pb2.TrainResponse(status="success")

    def GetPrediction(self, request, context):
        logging.info(f"Получение предсказания для модели: {request.model_name} с данными: {request.input_data}")

        if request.model_name not in self.models:
            context.set_details(f"Модель '{request.model_name}' не найдена.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return model_service_pb2.PredictionResponse(prediction=[])

        model = self.models[request.model_name]
        input_data = pd.DataFrame([request.input_data.fields])
        predictions = model.predict(input_data).tolist()
        return model_service_pb2.PredictionResponse(prediction=predictions)

    def DeleteModel(self, request, context):
        logging.info(f"Удаление модели: {request.model_name}")
        if request.model_name not in self.models:
            context.set_details(f"Модель '{request.model_name}' не найдена.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return model_service_pb2.DeleteResponse(status="failed")

        del self.models[request.model_name]
        return model_service_pb2.DeleteResponse(status="success")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_service_pb2_grpc.add_ModelServiceServicer_to_server(ModelService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("gRPC сервер запущен на порту 50051.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
