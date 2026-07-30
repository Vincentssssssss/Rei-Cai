import importlib


def test_langgraph_modules_importable():
    assert importlib.import_module("langgraph")
    assert importlib.import_module("langchain_core")
