def test_core_dependencies_import():
    import autogen_agentchat
    import autogen_core
    import autogen_ext
    import openlit
    import splunk_otel

    assert autogen_core.__name__ == "autogen_core"
    assert autogen_agentchat.__name__ == "autogen_agentchat"
    assert autogen_ext.__name__ == "autogen_ext"
    assert openlit.__name__ == "openlit"
    assert splunk_otel.__name__ == "splunk_otel"
