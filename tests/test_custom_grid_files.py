from custom_grids import load_custom_grids


def test_two_custom_grids_are_loaded_from_the_custom_grids_folder():
    grids = load_custom_grids()

    assert [name for name, _ in grids] == ["Custom Grid 1", "Custom Grid 2"]
    assert all(len(grid) == 10 and all(len(row) == 10 for row in grid) for _, grid in grids)
