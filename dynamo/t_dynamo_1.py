import json
import dynamodb as db
import copy


def t1():

    res = db.get_item("comments",
                      {
                          "comment_id": "7424f272-0e80-42d3-9f02-64301a7bd99f"
                      })
    print("Result = \n", json.dumps(res, indent=4, default=str))


def t2():

    res = db.find_by_template("comments", {
        "email": "um@never.com",
        "comment_id": "7424f272-0e80-42d3-9f02-64301a7bd99f",
        "tags": [
          "tt0018737",
          "Pandora's Box"
         ],
        "comment_content": "OMG testing idk",
        "datetime_str": "2021-11-01 05:03:19"
    })
    print("Result = \n", json.dumps(res, indent=4, default=str))


def t3():
    table_name = "comments"
    commenter = "izzi@fake.com"
    response = "hi KENYA"
    res = db.add_response(table_name, "37f42ee0-df46-41ad-93cb-f088e77fd817", "for@kenya.edu",
                         response)
    print("t3 -- res = ", json.dumps(res, indent=3))


def t4():
    tag = "Pandora's Box"
    res = db.find_by_tag(tag)
    print("Comments with tag \"Pandora's Box\" = \n", json.dumps(res, indent=3, default=str))


def t5():
    print("Do a projection ...\n")
    res = db.do_a_scan("comments",
                       None, None, "#c, comment_id", {"#c": "comment"})
    print("Result = \n", json.dumps(res, indent=4, default=str))


def t6():

    comment_id = "37f42ee0-df46-41ad-93cb-f088e77fd817"
    original_comment = db.get_item("comments", {"comment_id": comment_id})
    original_version_id = original_comment["version_id"]

    new_comment = copy.deepcopy(original_comment)

    try:
        res = db.write_comment_if_not_changed(original_comment, new_comment)
        print("First write returned: ", res)
    except Exception as e:
        print("First write exception = ", str(e))

    try:
        res = db.write_comment_if_not_changed(original_comment, new_comment)
        print("Second write returned: ", res)
    except Exception as e:
        print("Second write exception = ", str(e))


print("\nt1 PASSED\n")
t1()

print("\nt2 PASSED\n")
t2()

print("\nt3 PASSED\n")
t3()

print("\nt4 PASSED\n")
t4()

print("\nt5 PASSED\n")
t5()

print("\nt6 PASSED\n")
t6()
