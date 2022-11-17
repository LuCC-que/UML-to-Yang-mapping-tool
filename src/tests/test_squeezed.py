from factory.makeYang import makeYangInJson
import pytest
import pathlib
path = pathlib \
    .Path().resolve()


def test_container1():
    file_path = path.joinpath("resources")\
        .joinpath("container1.uml")

    Json = makeYangInJson(file_path).YangInJson

    if Json != {
        "_vhyFEFfpEe2mSIV9lJGM8w": {
            "name": "Class2",
            "profiles": {
                "RootElement": [
                    "1"
                ]
            },
            "attributes": {
                "@xmi:type": "uml:Property",
                "@xmi:id": "_E-MjUFfqEe2mSIV9lJGM8w",
                "@name": "attribut1",
                "type": {
                    "@xmi:type": "uml:PrimitiveType",
                    "@href": "pathmap://UML_LIBRARIES/UMLPrimitiveTypes.library.uml#String"
                }
            }
        }
    }:
        raise Exception("Wrong result produced")
