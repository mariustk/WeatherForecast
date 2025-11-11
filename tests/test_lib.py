from app.lib import wow_analysis


def test_wow_analysis_identifies_valid_windows():
    wave_heights = [0.5, 0.8, 1.2, 0.6, 0.4]
    go_no_go, start_indices = wow_analysis(wave_heights, task_duration=2, wave_height_limit=1.0)

    assert go_no_go == [True, True, False, True, True]
    assert start_indices == [0, 3]


def test_wow_analysis_handles_all_clear_window():
    wave_heights = [0.3, 0.4, 0.2, 0.5]
    go_no_go, start_indices = wow_analysis(wave_heights, task_duration=3, wave_height_limit=0.6)

    assert all(go_no_go)
    assert start_indices == [0, 1]


def test_wow_analysis_no_valid_window():
    wave_heights = [1.5, 1.2, 1.1]
    go_no_go, start_indices = wow_analysis(wave_heights, task_duration=1, wave_height_limit=1.0)

    assert go_no_go == [False, False, False]
    assert start_indices == []
