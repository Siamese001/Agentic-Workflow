"""Wave-J smoke: data authority loader singleton + sweep determinism."""

from agentic_core.L5_safety.identity.data_authority_loader import (
    DataAuthorityRecord,
    DataSourceKind,
    clear_active_data_authority,
    get_active_data_authority_ledger,
    get_active_data_authority_resolution,
    get_active_policy_version,
    set_active_data_authority_ledger,
)


def main() -> None:
    # 1. Bootstrap: empty ledger, trivially matches
    clear_active_data_authority()
    res0 = get_active_data_authority_resolution()
    res0b = get_active_data_authority_resolution()
    assert res0 is res0b, "must memoize within a run"
    assert res0.all_match is True
    assert res0.drifts == ()
    assert get_active_policy_version() == "v4.0.0-bootstrap"
    assert get_active_data_authority_ledger() == ()

    # 2. Load a ledger with one matching + one drifted record
    good = DataAuthorityRecord(
        source_id="rag_corpus_v1",
        kind=DataSourceKind.RAG_INDEX,
        content_digest="a" * 64,
        supply_chain_attestation="",
        expected_digest="a" * 64,
        policy_version="v4.1.0",
    )
    drift = DataAuthorityRecord(
        source_id="kb_corpus_v2",
        kind=DataSourceKind.KB_CORPUS,
        content_digest="b" * 64,
        supply_chain_attestation="",
        expected_digest="c" * 64,  # DRIFT
        policy_version="v4.1.0",
    )
    res1 = set_active_data_authority_ledger([good, drift], policy_version="v4.1.0")
    assert res1.all_match is False
    assert res1.drifts == ("kb_corpus_v2",)
    assert get_active_policy_version() == "v4.1.0"
    assert len(get_active_data_authority_ledger()) == 2

    # 3. Loader returns the cached resolution, not a rerun
    res1b = get_active_data_authority_resolution()
    assert res1b is res1, "post-swap resolution must be cached"

    # 4. policy_version required on swap
    try:
        set_active_data_authority_ledger([good], policy_version="")
    except ValueError:
        pass
    else:
        raise AssertionError("empty policy_version must raise")

    # 5. Clear restores bootstrap
    clear_active_data_authority()
    res2 = get_active_data_authority_resolution()
    assert res2.all_match is True
    assert res2.drifts == ()
    assert get_active_policy_version() == "v4.0.0-bootstrap"

    print("Wave-J smoke: OK (5 invariants)")


if __name__ == "__main__":
    main()
