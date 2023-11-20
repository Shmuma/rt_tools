from rt_tools import titles


def test_composers_mode():
    assert titles.ComposersMode.values() == ('prepend', "inside", "nothing")


def test_titles_inside_mode():
    gen = titles.TitlesGenerator(titles.ComposersMode.Inside)
    assert list(gen.add_track(1, "Bach", "Fuga")) == ["1. Bach: Fuga"]


def test_titles_nothing_mode():
    gen = titles.TitlesGenerator(titles.ComposersMode.Nothing)
    assert list(gen.add_track(1, "Bach", "Fuga")) == ["1. Fuga"]


def test_titles_prepend_mode():
    gen = titles.TitlesGenerator(titles.ComposersMode.Prepend)
    assert list(gen.add_track(1, "Bach", "Concerto - I. Allegro")) == [
        "Bach",
        "Concerto",
        "1. I. Allegro"
    ]
    assert list(gen.add_track(2, "Bach", "II. Adagio")) == ["2. II. Adagio"]
    assert list(gen.add_track(3, "Bach", "Concerto 2 - I. Presto")) == [
        "",
        "Concerto 2",
        "3. I. Presto"
    ]
    assert list(gen.add_track(4, "Bach", "II. Scherzo")) == ["4. II. Scherzo"]

    assert list(gen.add_track(5, "Chopin", "Prelude in C")) == [
        "",
        "Chopin",
        "5. Prelude in C"
    ]


def test_titles_prepend_duplicates():
    gen = titles.TitlesGenerator(titles.ComposersMode.Prepend)
    assert list(gen.add_track(1, "Bach", "Concerto - I. Allegro")) == [
        "Bach",
        "Concerto",
        "1. I. Allegro"
    ]
    assert list(gen.add_track(2, "Bach", "Concerto - II. Adagio")) == ["2. II. Adagio"]


def test_group_performers():
    assert list(titles.group_performers(["p1", "p1"])) == ["p1"]
    assert list(titles.group_performers(["p1", "p1", "p2"])) == [
        "1-2. p1",
        "3. p2"
    ]
