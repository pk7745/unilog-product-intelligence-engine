import os
import json
import pytest
import csv
from src import api, review_queue, pipeline_v2

@pytest.fixture(autouse=True)
def cleanup_decisions():
    # Save original review_decisions.json content if exists
    dec_path = "review/review_decisions.json"
    original = None
    if os.path.exists(dec_path):
        with open(dec_path, encoding="utf-8") as f:
            original = f.read()

    yield

    # Restore original decisions
    if original is not None:
        with open(dec_path, "w", encoding="utf-8") as f:
            f.write(original)
        review_queue.apply_review_decisions()
        pipeline_v2.run()
    elif os.path.exists(dec_path):
        os.remove(dec_path)
        review_queue.apply_review_decisions()
        pipeline_v2.run()

def test_review_queue_resolve_workflow():
    # Test A: RESOLVE action
    test_mpn = "TEST_MPN_RESOLVE_001"

    # Add test record to review_decisions.json
    res = api.post_review_decision({
        "mpn": test_mpn,
        "action": "RESOLVE",
        "fact_updates": []
    })
    assert res["status"] == "SUCCESS"
    assert res["action"] == "RESOLVE"

    # Verify GET /api/review/queue excludes test_mpn
    queue_resp = api.get_review_queue()
    queue_mpns = [item["mpn"] for item in queue_resp["items"]]
    assert test_mpn not in queue_mpns

    # Verify evidence cache status
    with open("cache/evidence_cache.json", encoding="utf-8") as f:
        cache = json.load(f)

    assert test_mpn in cache
    prod = cache[test_mpn]
    assert prod["verification_status"] == "VERIFIED"

def test_review_queue_leave_blank_workflow():
    # Test B: LEAVE_BLANK action
    test_mpn = "TEST_MPN_BLANK_002"

    res = api.post_review_decision({
        "mpn": test_mpn,
        "action": "LEAVE_BLANK",
        "fact_updates": []
    })
    assert res["status"] == "SUCCESS"
    assert res["action"] == "LEAVE_BLANK"

    # Verify GET /api/review/queue excludes test_mpn
    queue_resp = api.get_review_queue()
    queue_mpns = [item["mpn"] for item in queue_resp["items"]]
    assert test_mpn not in queue_mpns

    # Verify evidence cache status
    with open("cache/evidence_cache.json", encoding="utf-8") as f:
        cache = json.load(f)

    assert test_mpn in cache
    prod = cache[test_mpn]
    assert prod["verification_status"] == "CONFLICT"
    assert prod["human_review_status"] == "LEAVE_BLANK"

def test_review_queue_persistence():
    # Test C: Decision persistence across queue reload
    test_mpn = "TEST_PERSIST_MPN_003"

    api.post_review_decision({
        "mpn": test_mpn,
        "action": "RESOLVE",
        "fact_updates": []
    })

    # Simulate backend restart by re-reading decisions from disk
    queue_resp1 = api.get_review_queue()
    assert test_mpn not in [item["mpn"] for item in queue_resp1["items"]]

    # Reload review queue module directly
    queue_items = review_queue.load_qa_review_queue()
    assert test_mpn not in [item["Mfg_Part_Num"] for item in queue_items]
