from .context import pycoornet


def test_app(capsys, example_fixture):
    pycoornet.App.run()
    captured = capsys.readouterr()

    assert "Hello World" in captured.out
