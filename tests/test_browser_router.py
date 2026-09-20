from execution.action_router import ActionRouter


def test_browser_start_and_close():

    router = ActionRouter()

    result = router.execute({
        "action": "browser_start"
    })

    assert result.success is True
    assert result.executor == "playwright"

    close_result = router.execute({
        "action": "browser_close"
    })

    assert close_result.success is True
    assert close_result.executor == "playwright"


def test_browser_open_url():

    router = ActionRouter()

    router.execute({
        "action": "browser_start"
    })

    result = router.execute({
        "action": "browser_open_url",
        "url": "https://example.com",
    })

    assert result.success is True
    assert result.executor == "playwright"

    assert result.data["url"] == (
        "https://example.com/"
    )

    router.execute({
        "action": "browser_close"
    })


def test_browser_get_title():

    router = ActionRouter()

    router.execute({
        "action": "browser_start"
    })

    router.execute({
        "action": "browser_open_url",
        "url": "https://example.com",
    })

    result = router.execute({
        "action": "browser_get_title"
    })

    assert result.success is True
    assert result.data["title"] == (
        "Example Domain"
    )

    router.execute({
        "action": "browser_close"
    })


def test_browser_get_text():

    router = ActionRouter()

    router.execute({
        "action": "browser_start"
    })

    router.execute({
        "action": "browser_open_url",
        "url": "https://example.com",
    })

    result = router.execute({
        "action": "browser_get_text",
        "selector": "body",
    })

    assert result.success is True

    assert "Example Domain" in (
        result.data["text"]
    )

    router.execute({
        "action": "browser_close"
    })


def test_browser_state():

    router = ActionRouter()

    router.execute({
        "action": "browser_start"
    })

    router.execute({
        "action": "browser_open_url",
        "url": "https://example.com",
    })

    result = router.execute({
        "action": "browser_state"
    })

    assert result.success is True

    assert (
        result.data["browser_open"]
        is True
    )

    assert (
        result.data["current_url"]
        == "https://example.com/"
    )

    router.execute({
        "action": "browser_close"
    })