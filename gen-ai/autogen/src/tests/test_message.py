from message import Message


def test_message_stores_content():
    message = Message(content="Go!")
    assert message.content == "Go!"
