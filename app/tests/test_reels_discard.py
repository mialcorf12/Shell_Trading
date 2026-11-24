from ideas_core import reels

HEADER = "# Reels\n\nRegla.\n\n"
U1 = "https://www.instagram.com/reels/AAA111/"
U2 = "https://www.instagram.com/reels/BBB222/"
U3 = "https://www.instagram.com/reels/CCC333/"


def write_file(tmp_path, new, done, discarded):
    path = tmp_path / "reels.md"
    path.write_text(reels.render(HEADER, new, done, discarded), encoding="utf-8")
    return path


def test_render_includes_discarded_section_sorted():
    text = reels.render(HEADER, [], {}, {U2: ("reel_BBB222.md", "promo"), U1: ("-", "dup")})
    assert "## C) Links descartados" in text
    assert text.index(U1) < text.index(U2)
    assert f"- {U2} → reel_BBB222.md | promo" in text


def test_parse_discarded_reads_draft_and_reason():
    text = reels.render(HEADER, [], {}, {U1: ("reel_AAA111.md", "promo")})
    assert reels.parse_discarded(text) == {U1: ("reel_AAA111.md", "promo")}


def test_parse_ignores_discarded_items_in_new_and_done_sections():
    text = reels.render(HEADER, [], {}, {U1: ("-", "dup")})
    new, done = reels.parse(text)
    assert U1 not in new and U1 not in done


def test_check_removes_new_link_that_is_discarded():
    pending, removed, discarded_hit = reels.check([U1, U3], {}, {U1: ("-", "dup")})
    assert pending == [U3]
    assert discarded_hit == [U1]
    assert removed == []


def test_run_check_deletes_draft_of_discarded_link(tmp_path):
    draft = tmp_path / "reel_AAA111.md"
    draft.write_text("x", encoding="utf-8")
    path = write_file(tmp_path, [U1, U3], {}, {U1: ("reel_AAA111.md", "promo")})

    result = reels.run_check(path)

    assert result["discarded_hit"] == [U1]
    assert not draft.exists()
    new, _ = reels.parse(path.read_text(encoding="utf-8"))
    assert new == [U3]
    assert U1 in reels.parse_discarded(path.read_text(encoding="utf-8"))


def test_run_check_tolerates_missing_draft_file(tmp_path):
    path = write_file(tmp_path, [U1], {}, {U1: ("reel_AAA111.md", "promo")})
    result = reels.run_check(path)
    assert result["discarded_hit"] == [U1]


def test_mark_discarded_moves_processed_link_to_c_and_deletes_its_draft(tmp_path):
    draft = tmp_path / "reel_BBB222.md"
    draft.write_text("x", encoding="utf-8")
    path = write_file(tmp_path, [], {U2: "reel_BBB222.md"}, {})

    reels.run_discard(path, U2, "promo")

    assert not draft.exists()
    text = path.read_text(encoding="utf-8")
    assert reels.parse(text) == ([], {})
    assert reels.parse_discarded(text) == {U2: ("reel_BBB222.md", "promo")}


def test_mark_discarded_from_new_without_draft_records_dash(tmp_path):
    path = write_file(tmp_path, [U3], {}, {})
    reels.run_discard(path, U3, "fuera de alcance")
    text = path.read_text(encoding="utf-8")
    assert reels.parse(text) == ([], {})
    assert reels.parse_discarded(text) == {U3: ("-", "fuera de alcance")}


def test_mark_discarded_keeps_ideas_file_untouched(tmp_path):
    # Done value pointing to an Ideas file (not a draft): never delete it.
    ideas = tmp_path / "FVG_01.md"
    ideas.write_text("x", encoding="utf-8")
    path = write_file(tmp_path, [], {U2: "FVG_01.md"}, {})
    reels.run_discard(path, U2, "promo")
    assert ideas.exists()
