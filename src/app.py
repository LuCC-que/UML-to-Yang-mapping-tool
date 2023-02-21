import pathlib
from flask import Flask
from flask_smorest import Api

import pathlib

from factory.BuildYang import BuildYang
from factory.WriteYang import WriteYang
from resources.xmls_req import blp as xmlBluprint


def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "UML to yang translator services"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    api = Api(app)
    print("start")

    api.register_blueprint(xmlBluprint)

    return app


if __name__ == "__main__":
    import os
    import glob
    if not os.path.exists("Yangs"):
        os.makedirs("Yangs")

    files = glob.glob(os.path.join("local_XMLS", 'p24.uml'))

    for file in files:
        path = pathlib.Path().resolve().joinpath(file)
        ob = BuildYang(path)
        writeYang = WriteYang(ob.Graph, ob.RenderStart)

        print(writeYang.output)
        # output_path = os.path.join("Yangs", file[11:-4]+".txt")

        # with open(output_path, 'w', encoding="utf8") as file:
        #     result = writeYang(ob.Classes, ob.Associations)
        #     file.write(result)
        # print(result)
