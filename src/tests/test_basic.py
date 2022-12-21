from factory.makeYang import makeYangInJson
from factory.WriteYang import writeYang
import pathlib
path = pathlib \
    .Path().resolve()


def format_and_compare(str1, str2) -> bool:
    str1 = str1.replace("\t", "").replace("\n", "").replace(" ", "")
    str2 = str2.replace("\t", "").replace("\n", "").replace(" ", "")

    return str1 == str2


def test_container1():

    expect = \
        "container Class2 {\
            leaf attribut1 {\
            type String;\
            }\
        }".replace(" ", "")

    file_path = path.joinpath("local_XMLs").joinpath("container1.uml")
    ob = makeYangInJson(file_path)
    result = writeYang(ob.Classes, ob.Associations)

    assert format_and_compare(expect, result)
