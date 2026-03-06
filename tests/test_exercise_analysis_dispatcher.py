from app.services.exercise_analysis.dispatcher import create_analyzer


def test_dispatcher_knee_extension_counts_rep():
    analyzer = create_analyzer("KNEE_EXTENSION_V1")

    params = {"low_deg": 95, "high_deg": 170, "min_hold_ms": 0, "hysteresis_deg": 0}

    # sequência que faz 1 rep: baixa <=95 e depois sobe >=170
    seq = [175, 160, 120, 95, 90, 110, 150, 170, 175]
    for i, rom in enumerate(seq):
        out = analyzer.run(rom, params, ts_ms=1000 + i * 10)

    assert out["reps"] == 1
    assert "alertas" in out
    # garante que são mensagens (não códigos)
    assert all(isinstance(a, str) for a in out["alertas"])
