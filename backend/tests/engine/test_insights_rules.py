from app.engine.insights.rules import select_top_insights
from app.engine.insights.types import Insight


def _insight(key, category, score):
    return Insight(key=key, category=category, title=key, description="", score=score)


def test_select_top_insights_picks_highest_scores():
    candidates = [
        _insight("a", "cat1", 10),
        _insight("b", "cat2", 90),
        _insight("c", "cat3", 50),
        _insight("d", "cat4", 30),
    ]

    result = select_top_insights(candidates, min_n=2, max_n=3)

    assert [i.key for i in result] == ["b", "c", "d"]


def test_select_top_insights_avoids_category_repeats_when_possible():
    candidates = [
        _insight("a", "ranking", 90),
        _insight("b", "ranking", 85),
        _insight("c", "margem_negativa", 70),
    ]

    result = select_top_insights(candidates, min_n=2, max_n=3)

    assert [i.key for i in result] == ["a", "c"]


def test_select_top_insights_allows_repeat_category_to_reach_min_n():
    candidates = [
        _insight("a", "ranking", 90),
        _insight("b", "ranking", 85),
    ]

    result = select_top_insights(candidates, min_n=2, max_n=3)

    assert [i.key for i in result] == ["a", "b"]


def test_select_top_insights_returns_fewer_than_min_n_when_not_enough_candidates():
    result = select_top_insights([_insight("a", "ranking", 90)], min_n=2, max_n=3)

    assert [i.key for i in result] == ["a"]
