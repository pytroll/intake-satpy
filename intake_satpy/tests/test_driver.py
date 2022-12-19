def test_driver_registration():
    import intake

    assert hasattr(intake, "open_satpy")
