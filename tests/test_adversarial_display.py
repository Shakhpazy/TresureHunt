from adversarial.display import format_move, format_scoreboard, render
from tests.adversarial_helpers import make_state


def board_rows(text):
    return text.split("\n")[1:]  # drop the column header


def test_every_kind_of_cell_has_its_own_glyph():
    state = make_state(
        "A#X.",
        "..TB",
    )
    text = render(state)
    glyphs = [line.split()[1:] for line in board_rows(text)]
    assert glyphs == [["A", "#", "X", "."], [".", ".", "T", "B"]]


def test_columns_line_up_with_their_numbers_even_past_ten():
    state = make_state("A.........T.....B")  # 17 columns
    header, row = render(state).split("\n")
    for column, glyph in ((0, "A"), (10, "T"), (16, "B")):
        position = row.index(glyph) if glyph != "T" else row.index("T")
        assert header[position] == str(column)[-1]  # the last digit sits right above the glyph


def test_collected_treasure_disappears_from_the_board():
    state = make_state("AT.B")
    state.make((0, 1))
    assert "T" not in render(state).split("\n")[1]


def test_colour_is_off_by_default_and_wraps_glyphs_when_asked():
    state = make_state("A#TB")
    assert "\033[" not in render(state)
    coloured = render(state, color=True)
    assert "\033[" in coloured
    assert coloured.count("\033[0m") == 4  # one reset per coloured glyph


def test_scoreboard_and_move_lines():
    state = make_state("A.TB")
    assert "A=0  B=0" in format_scoreboard(state) and "ply=0/200" in format_scoreboard(state)
    line = format_move(5, 0, "Alpha-Beta d4 E1", (3, 4), (3, 5), True, "value=98")
    assert line == "ply   5 | A (Alpha-Beta d4 E1) (3, 4) -> (3, 5) +treasure | value=98"
    assert "passes" in format_move(6, 1, "random", (0, 0), None, False)
