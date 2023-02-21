'''
These are the test set of the most basic in TR-531

from page 15 - page 17
'''

from factory.BuildYang import BuildYang
from factory.WriteYang import WriteYang
import pathlib
path = pathlib \
    .Path().resolve()

dir_path = path.joinpath("local_XMLs")


def format_and_compare(str1, str2) -> bool:
    str1 = str1.replace("\t", "").replace("\n", "").replace(" ", "")
    str2 = str2.replace("\t", "").replace("\n", "").replace(" ", "")

    return str1 == str2


def test_multiAsso():

    expect =                                    \
        "container Class4 {                     \
                leaf name{                      \
                        type String;            \
                }                               \
                grouping Class5 {               \
                        leaf value{             \
                                type String;    \
                        }                       \
                }                               \
                grouping Class7 {               \
                        leaf value{             \
                                type String;    \
                        }                       \
                        uses Class5;            \
                }                               \
        }                                       \
        grouping Class5 {                       \
                leaf value{                     \
                        type String;            \
                }                               \
        }"

    file_path = dir_path.joinpath("multiAsso.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_multiAsso_4():

    expect =                                    \
        "container Class13 {                    \
                leaf attr1{                     \
                        type String;            \
                }                               \
                grouping Class14 {              \
                        leaf attr2{             \
                                type String;    \
                        }                       \
                        uses Class16;           \
                        uses Class18;           \
                }                               \
        }                                       \
        grouping Class18 {                      \
                leaf attr3{                     \
                        type String;            \
                }                               \
        }                                       \
        list Class16 {                          \
                leaf attr5{                     \
                        type String;            \
                }                               \
                grouping Class18 {              \
                        leaf attr3{             \
                                type String;    \
                        }                       \
                }                               \
        }                                       \
        container Class3 {                      \
                leaf name{                      \
                        type String;            \
                }                               \
                uses Class4;                    \
                uses Class5;                    \
                list Class6 {                   \
                        leaf thenum{            \
                                type Integer;   \
                        }                       \
                        uses Class4;            \
                        uses Class5;            \
                }                               \
        }                                       \
        grouping Class5 {                       \
                leaf name{                      \
                        type String;            \
                }                               \
        }                                       \
        grouping Class4 {                       \
                leaf number{                    \
                        type Integer;           \
                }                               \
        }"

    file_path = dir_path.joinpath("multiAsso-4.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p15():

    expect =                        \
        "container SubClass {       \
        leaf attribute5{            \
                type String;        \
                mandatory true;     \
        }                           \
        leaf attribute6{            \
                type String;        \
                mandatory true;     \
        }                           \
        uses SuperClass1;           \
        uses SuperClass2;           \
    }                               \
    grouping SuperClass2 {          \
        leaf-list attribute3{       \
                type String;        \
                min-elements 2;     \
                max-elements 4;     \
        }                           \
        leaf-list attribute4{       \
                type String;        \
                min-elements 2;     \
        }                           \
    }                               \
    grouping SuperClass1 {          \
        leaf attribute1{            \
                type String;        \
        }                           \
        leaf attribute2{            \
                type String;        \
        }                           \
    }"

    file_path = dir_path.joinpath("p15.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_additonal_root():
    '''
    if the RootElement attached to it has name and description
    this usually represent the existing class is the group
    and we use the information inside the rootelement to
    generate a container to use this group

    see p16 in the TR-531
    '''

    expect =                                                        \
        'container Root {                                           \
            presence "Presence indicates data-store is enabled";    \
            uses RootClass;                                         \
        }                                                           \
        grouping RootClass {                                        \
                leaf attribute1{                                    \
                        type Integer;                               \
                        mandatory true;                             \
                }                                                   \
                leaf attribute2{                                    \
                        type String;                                \
                        mandatory true;                             \
                }                                                   \
        }'

    file_path = dir_path.joinpath("p16.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_additonal_root2():
    '''
    this is list case

    see p17 in the TR-531
    '''

    expect =                                \
        'list Root {                        \
            presence "this is list";        \
            uses RootClass;                 \
        }                                   \
        grouping RootClass {                \
                leaf attribute1{            \
                        type Integer;       \
                        mandatory true;     \
                }                           \
                leaf attribute2{            \
                        type String;        \
                        mandatory true;     \
                }                           \
        }'

    file_path = dir_path.joinpath("p17a.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p22():
    '''
    this is enum case and default value cases

    see p22 in the TR-531
    '''

    expect =                                            \
        'grouping Class1 {                              \
                leaf class1ID{                          \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
                leaf attribute1{                        \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
                leaf-list attribute2{                   \
                        type String;                    \
                        min-elements 2;                 \
                        max-elements 6;                 \
                }                                       \
                leaf attribute3{                        \
                        type Boolean;                   \
                        mandatory true;                 \
                        default true;                   \
                }                                       \
                leaf attribute4{                        \
                        type enumeration {              \
                                enum LITERAL_1;         \
                                enum LITERAL_2;         \
                                enum LITERAL_3;         \
                        }                               \
                        default LITERAL_2;              \
                }                                       \
        }'

    file_path = dir_path.joinpath("p22.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p22_i():
    '''
    this is enum case and default value cases

    see p22 in the TR-531
    '''

    expect =                                            \
        'grouping Class1 {                              \
                leaf class1ID{                          \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
                leaf attribute1{                        \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
                leaf-list attribute2{                   \
                        type String;                    \
                        min-elements 2;                 \
                        max-elements 6;                 \
                        config false;                   \
                }                                       \
                leaf attribute3{                        \
                        type Boolean;                   \
                        mandatory true;                 \
                        default true;                   \
                }                                       \
                leaf attribute4{                        \
                        type enumeration {              \
                                enum LITERAL_1;         \
                                enum LITERAL_2;         \
                                enum LITERAL_3;         \
                        }                               \
                        default LITERAL_2;              \
                }                                       \
        }'

    file_path = dir_path.joinpath("p22-i.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p23():
    '''
    this is list case

    see p23 in the TR-531
    '''

    expect =                                    \
        'list UniqueExample {                   \
                key uniqueAttribute;            \
                unique uniqueAttribute;         \
                uses UniqueExample;             \
        }                                       \
        grouping UniqueExample {                \
                leaf uniqueAttribute{           \
                        type String;            \
                        mandatory true;         \
                }                               \
        }'

    file_path = dir_path.joinpath("p23.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p24():
    '''
    this is UniqueSetExample case

    see p24 in the TR-531
    '''

    expect =                                    \
        'list UniqueSetExample {                \
                key attribute1;                 \
                unique attribute1 attribute2;   \
                unique attribute2 attribute3;   \
                uses UniqueSetExample;          \
        }                                       \
        grouping UniqueSetExample {             \
                leaf attribute1{                \
                        type String;            \
                        config false;           \
                }                               \
                leaf attribute2{                \
                        type Integer;           \
                }                               \
                leaf attribute3{                \
                        type String;            \
                }                               \
        }'

    file_path = dir_path.joinpath("p24.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)


def test_p26():
    '''
    this is UniqueSetExample case

    see p26 in the TR-531
    '''

    expect =                                            \
        'grouping ClassR {                              \
                container attributeCurrent {            \
                        uses DataTypeA;                 \
                }                                       \
                list attributePotential {               \
                        uses DataTypeA;                 \
                }                                       \
        }                                               \
        grouping DataTypeA {                            \
                leaf attribute1{                        \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
                leaf attribute2{                        \
                        type Integer;                   \
                }                                       \
                leaf attribute3{                        \
                        type String;                    \
                        mandatory true;                 \
                }                                       \
        }'

    file_path = dir_path.joinpath("p26.uml")
    ob = BuildYang(file_path)
    result = WriteYang(ob.Graph, ob.RenderStart)

    assert format_and_compare(expect, result.output)
