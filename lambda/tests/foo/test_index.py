from foo.index import handler


class TestIndex:
    def test_handler(self) -> None:
        handler(None, None)
