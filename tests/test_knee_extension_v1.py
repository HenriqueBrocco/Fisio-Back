from app.services.exercise_analysis.knee_extension_v1 import (
    KneeExtensionState,
    update_knee_extension,
)


def test_knee_extension_counts_rep():
    st = KneeExtensionState()
    params = {"low_deg": 95, "high_deg": 170, "min_hold_ms": 0, "hysteresis_deg": 0}

    # começa estendido
    seq = [175, 172, 160, 120, 95, 90, 92, 110, 150, 170, 175]
    for i, rom in enumerate(seq):
        update_knee_extension(rom, st, params, ts_ms=1000 + i * 10)

    assert st.reps == 1


def test_knee_extension_no_rep_if_never_reaches_high():
    st = KneeExtensionState()
    params = {"low_deg": 95, "high_deg": 170, "min_hold_ms": 0, "hysteresis_deg": 0}

    seq = [175, 150, 120, 95, 90, 100, 130, 160, 165]  # não chega 170
    for i, rom in enumerate(seq):
        update_knee_extension(rom, st, params, ts_ms=1000 + i * 10)

    assert st.reps == 0
