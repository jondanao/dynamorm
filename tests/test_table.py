"""These tests require dynamo local running"""
import pytest

from marshmallow import fields

from dynamallow.table import HashKeyExists, InvalidSchemaField, _field_to_dynamo_type


def test_field_to_dynamo_type():
    assert _field_to_dynamo_type(fields.Number()) == 'N'
    assert _field_to_dynamo_type(fields.Decimal()) == 'N'
    assert _field_to_dynamo_type(fields.Raw()) == 'B'
    assert _field_to_dynamo_type(fields.DateTime()) == 'S'


def test_table_creation_deletion(TestModel, dynamo_local):
    """Creating, detecting and deleting tables should work"""
    assert not TestModel.Table.exists
    assert TestModel.Table.create()
    assert TestModel.Table.exists
    assert TestModel.Table.delete()
    assert not TestModel.Table.exists


def test_put_get(TestModel, TestModel_table, dynamo_local):
    """Putting and getting an item should work"""
    TestModel.put({"foo": "first", "bar": "one", "baz": "lol", "count": 123})
    first_one = TestModel.get(foo="first", bar="one")
    assert isinstance(first_one, TestModel)
    assert first_one.baz == 'lol' and first_one.count == 123


def test_put_batch(TestModel, TestModel_table, dynamo_local):
    """Batch putting items should work"""
    TestModel.put_batch(
        {"foo": "first", "bar": "two", "baz": "wtf", "count": 321},
        {"foo": "second", "bar": "one", "baz": "bbq", "count": 456},
    )
    second_one = TestModel.get(foo="second", bar="one")
    assert isinstance(second_one, TestModel)
    assert second_one.baz == 'bbq' and second_one.count == 456


def test_get_non_existant(TestModel, TestModel_table, dynamo_local):
    """Getting a non-existant item should return None"""
    assert TestModel.get(foo="fifth", bar="derp") is None


def test_object_syntax(TestModel, TestModel_table, dynamo_local):
    """Putting (saving) an item using the object syntax should work"""
    third_three = TestModel(foo="third", bar="three", baz="idk", count=7)
    third_three.save()

    assert TestModel.get(foo="third", bar="three").baz == "idk"


def test_put_unique(TestModel, TestModel_table, dynamo_local):
    """Putting an item with a unique constraint should work"""
    TestModel.put({"foo": "third", "bar": "three", "baz": "fuu", "count": 8})

    assert TestModel.get(foo="third", bar="three").baz == "fuu"

    with pytest.raises(HashKeyExists):
        TestModel.put_unique({"foo": "third", "bar": "three", "baz": "waa", "count": 9})

def test_get_invalid_field(TestModel):
    """Calling .get on an invalid field should result in an exception"""
    with pytest.raises(InvalidSchemaField):
        TestModel.get(bbq="wtf")


def test_query(TestModel, TestModel_table, dynamo_local):
    """Querying should return the expected values"""

    TestModel.put_batch(
        {"foo": "first", "bar": "two", "baz": "wtf", "count": 321},
        {"foo": "second", "bar": "one", "baz": "bbq", "count": 456},
        {"foo": "third", "bar": "three", "baz": "omg", "count": 123},
    )

    #results = list(TestModel.query(
