import grpc
from flask import Blueprint, Flask, jsonify, request

from grpcService import model_service_pb2, model_service_pb2_grpc

api = Blueprint("api", __name__)


def get_grpc_channel():
    return grpc.insecure_channel("localhost:50051")


@api.route("/model_list", methods=["GET"])
def model_list():
    with get_grpc_channel() as channel:
        stub = model_service_pb2_grpc.ModelServiceStub(channel)
        response = stub.GetModelList(model_service_pb2.Empty())
        return jsonify({"types": response.types})


@api.route("/model", methods=["POST"])
def train_model():
    data = request.json
    with get_grpc_channel() as channel:
        stub = model_service_pb2_grpc.ModelServiceStub(channel)
        response = stub.TrainModel(
            model_service_pb2.TrainRequest(
                model_type=data["model_type"], params=data["params"]
            )
        )
        return jsonify({"status": response.status}), 200


@api.route("/model", methods=["GET"])
def get_prediction():
    model_name = request.args.get("model_name")
    input_data = request.args.get("input_data")
    with get_grpc_channel() as channel:
        stub = model_service_pb2_grpc.ModelServiceStub(channel)
        response = stub.GetPrediction(
            model_service_pb2.PredictionRequest(
                model_name=model_name, input_data=input_data
            )
        )
        return jsonify({"prediction": response.prediction}), 200


@api.route("/model", methods=["DELETE"])
def delete_model():
    model_name = request.json.get("model_name")
    with get_grpc_channel() as channel:
        stub = model_service_pb2_grpc.ModelServiceStub(channel)
        response = stub.DeleteModel(
            model_service_pb2.DeleteRequest(model_name=model_name)
        )
        return jsonify({"status": response.status}), 200


app = Flask(__name__)
app.register_blueprint(api)
