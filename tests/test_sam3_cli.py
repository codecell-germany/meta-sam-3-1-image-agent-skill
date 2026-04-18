from sam3_cli import find_contained_box_removals, overlap_ratio_of_smaller_box


def test_overlap_ratio_of_smaller_box_uses_smaller_area():
    inner = [10, 10, 20, 20]
    outer = [0, 0, 30, 30]

    assert overlap_ratio_of_smaller_box(inner, outer) == 1.0


def test_find_contained_box_removals_prefers_outer_box():
    boxes = [
        [0, 0, 100, 100],
        [10, 10, 90, 90],
        [150, 150, 220, 220],
    ]

    removals = find_contained_box_removals(boxes, overlap_threshold=0.9)

    assert removals == [
        {
            "removed_index": 1,
            "kept_index": 0,
            "relation": "contained_by_larger_box",
            "overlap_ratio_of_smaller": 1.0,
        }
    ]


def test_find_contained_box_removals_ignores_partial_overlap():
    boxes = [
        [0, 0, 100, 100],
        [50, 50, 150, 150],
    ]

    removals = find_contained_box_removals(boxes, overlap_threshold=0.9)

    assert removals == []
