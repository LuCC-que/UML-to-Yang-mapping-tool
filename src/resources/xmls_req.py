from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint
from factory.makeYang import makeYangInJson
from factory.WriteYang import writeYang

blp = Blueprint("xmlRequest",
                __name__,
                description="receving xml and respon"
                "ding translation result")


@blp.route("/xml")
class xmlRequest(MethodView):
    def get(self):
        xml_data = request.data
        ob = makeYangInJson(None, xml_data)
        result = writeYang(ob.Classes, ob.Associations)
        print(result)
        return result
