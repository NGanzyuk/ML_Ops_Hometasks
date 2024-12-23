import pandas as pd
from flask import Response, request
from flask_restx import Api, Resource, fields

from service import Service

api = Api(version="0.1.0", title="Model API", description="API для ML моделей")

service = Service()

# Определение моделей для API
typesOutput = api.model("Types output",
                        {"types": fields.List(description="Доступные типы моделей", cls_or_instance=fields.String)})
infoModel = api.model("Model info",
                      {"id": fields.String(), "type": fields.String(), "params": fields.Wildcard(fields.String)})
instancesOutput = api.model("Instances output", {
    "instances": fields.List(description="Доступные экземпляры моделей", cls_or_instance=fields.Nested(infoModel))})
predictionOutput = api.model("Prediction output",
                             {"predict": fields.List(description="Список предсказаний", cls_or_instance=fields.Float)})
modelNameOutput = api.model("Model name output",
                            {"model_name": fields.String(description="Уникальный идентификатор модели")})
errorOutput = api.model("Error output", {"message": fields.String(description="Сообщение об ошибке")})

modelRetrainInput = api.model("Model retrain input", {
    "data": fields.List(description="DataFrame с признаками в формате JSON",
                        cls_or_instance=fields.Wildcard(fields.String)),
    "target": fields.List(description="Целевая переменная", cls_or_instance=fields.Float),
    "model_name": fields.String(description="Уникальный идентификатор модели для переобучения"),
})

modelFitInput = api.model("Model fit input", {
    "data": fields.List(description="DataFrame с признаками в формате JSON",
                        cls_or_instance=fields.Wildcard(fields.String)),
    "target": fields.List(description="Целевая переменная", cls_or_instance=fields.Float),
    "model_type": fields.String(description="Тип модели для обучения"),
    "params": fields.Wildcard(description="Параметры для обучения модели", cls_or_instance=fields.String),
})

modelPredictInput = api.model("Model predict input", {
    "data": fields.List(description="DataFrame с признаками в формате JSON",
                        cls_or_instance=fields.Wildcard(fields.String)),
    "model_name": fields.String(description="Уникальный идентификатор модели для получения предсказания"),
})

modelDeleteInput = api.model("Model delete input",
                             {"model_name": fields.String(description="Уникальный идентификатор модели для удаления")})


# Определение маршрутов API
@api.route("/status")
class Status(Resource):
    def get(self):
        return {"status": "running"}, 200


@api.route("/model_list")
class ModelList(Resource):
    @api.marshal_with(typesOutput)
    def get(self):
        """Получить все возможные типы моделей."""
        return {"types": service.getModelList()}


@api.route("/model_instances")
class ModelInstances(Resource):
    @api.marshal_with(instancesOutput)
    def get(self):
        """Получить информацию обо всех обученных моделях."""
        return {"instances": service.getModelInstances()}


@api.route("/model_retrain")
class ModelRetrain(Resource):
    @api.response(200, "Успешно переобучено", modelNameOutput)
    @api.response(404, "Ошибка: Не найдено", errorOutput)
    @api.expect(modelRetrainInput)
    def post(self):
        """Переобучить модель на новых данных."""
        data = pd.DataFrame(request.json["data"])
        target = request.json["target"]
        modelName = request.json["model_name"]
        try:
            modelName = service.modelRetrain(data, target, modelName)
        except ValueError as e:
            return {"message": str(e)}, 404
        return {"model_name": modelName}


@api.route("/model")
class ModelApi(Resource):
    @api.response(200, "Успешно обучено", modelNameOutput)
    @api.response(404, "Ошибка: Не найдено", errorOutput)
    @api.expect(modelFitInput)
    def post(self):
        """Обучить модель с параметрами и данными."""
        data = pd.DataFrame(request.json["data"])
        target = request.json["target"]
        modelType = request.json["model_type"]
        params = request.json["params"]
        try:
            modelName = service.modelTrain(data, target, modelType, params)
        except ValueError as e:
            return {"message": str(e)}, 404
        return {"model_name": modelName}

    @api.response(200, "Успешно предсказано", predictionOutput)
    @api.response(404, "Ошибка: Не найдено", errorOutput)
    @api.expect(modelPredictInput)
    def get(self):
        """Получить предсказания модели по идентификатору модели."""
        data = pd.DataFrame(request.json["data"])
        modelName = request.json["model_name"]
        try:
            predict = service.getModel(data, modelName)
        except ValueError as e:
            return {"message": str(e)}, 404
        return {"predict": predict}

    @api.response(204, "Удалено")
    @api.expect(modelDeleteInput)
    def delete(self):
        """Удалить модель из базы данных по идентификатору модели."""
        modelName = request.json["model_name"]
        service.deleteModel(modelName)
        return Response(status=204)
