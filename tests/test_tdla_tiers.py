from src.tdla.tiers import Tier, UpdateRecord, stored_size_kb, tier_for_age_days


def test_tier_for_age_hot():
    for age in range(0, 8):
        assert tier_for_age_days(age) == Tier.HOT


def test_tier_for_age_warm():
    for age in range(8, 91):
        assert tier_for_age_days(age) == Tier.WARM


def test_tier_for_age_cold():
    for age in range(91, 731):
        assert tier_for_age_days(age) == Tier.COLD


def test_tier_for_age_archive():
    for age in (731, 732, 1000, 10000, 10**9):
        assert tier_for_age_days(age) == Tier.ARCHIVE


def test_tier_boundaries_exact():
    assert tier_for_age_days(7) == Tier.HOT
    assert tier_for_age_days(8) == Tier.WARM
    assert tier_for_age_days(90) == Tier.WARM
    assert tier_for_age_days(91) == Tier.COLD
    assert tier_for_age_days(730) == Tier.COLD
    assert tier_for_age_days(731) == Tier.ARCHIVE


def test_stored_size_monotonic_with_tier():
    record = UpdateRecord(
        id=1, day=0, size_kb=100.0, segment_km=1.0, kind="modified"
    )
    hot = stored_size_kb(record, Tier.HOT)
    warm = stored_size_kb(record, Tier.WARM)
    cold = stored_size_kb(record, Tier.COLD)
    archive = stored_size_kb(record, Tier.ARCHIVE)
    assert hot > warm > cold > archive
