"""Seed demo data into CloudWatch so QA can practise the runbook without a live deploy.

Creates (region ap-southeast-1):
  - log group  /shoeshub/qa/demo   (7-day retention) + ~140 JSON request logs
  - metric filter error-count      -> ShoesHub/QA ErrorCountFromLogs
  - custom metrics ShoesHub/QA     {RequestLatencyP99Ms, RequestsPerSecond, ErrorCount, OrdersPlaced}
  - alarm      shoeshub-qa-demo-errors
  - dashboard  shoeshub-qa-demo

Usage:
  pip install boto3
  python scripts/seed_cloudwatch_demo.py             # seed
  python scripts/seed_cloudwatch_demo.py --teardown  # delete everything

Auth: default boto3 session (honours AWS_PROFILE / `aws login` credentials).
Cost: a few cents; run --teardown when finished. See docs/QA_AWS_RUNBOOK.md section 11.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime, timezone

import boto3

REGION = "ap-southeast-1"
LOG_GROUP = "/shoeshub/qa/demo"
NAMESPACE = "ShoesHub/QA"
ALARM = "shoeshub-qa-demo-errors"
DASHBOARD = "shoeshub-qa-demo"
DIMS = [{"Name": "Environment", "Value": "qa"}]


def _jitter(seed: float, lo: float, hi: float) -> float:
    """Deterministic pseudo-random value in [lo, hi) — no `random` module needed."""
    frac = math.sin(seed * 12.9898 + 7.13) * 43758.5453
    frac -= math.floor(frac)
    return lo + (hi - lo) * frac


def _log_events(now: float) -> list[dict]:
    paths = ["/api/products", "/api/products/7", "/api/cart", "/api/orders",
             "/api/auth/login", "/api/discount-codes/validate"]
    posts = {"/api/orders", "/api/auth/login", "/api/cart", "/api/discount-codes/validate"}
    events: list[dict] = []
    count, start = 140, now - 45 * 60
    for i in range(count):
        ts = start + i * (45 * 60 / count)
        frac = i / count
        spike = 0.55 < frac < 0.72
        latency = 25 + 180 * frac + (620 if spike else 0) + _jitter(i, -12, 45)
        path = paths[int(_jitter(i + 7, 0, len(paths))) % len(paths)]
        method = "POST" if path in posts else "GET"
        ok = 201 if method == "POST" else 200
        if spike and _jitter(i + 3, 0, 1) < 0.42:
            status, level, message = 500, "ERROR", "request_failed"
        elif latency >= 1000:
            status, level, message = ok, "WARNING", "request"
        else:
            status, level, message = ok, "INFO", "request"
        events.append({"timestamp": int(ts * 1000), "message": json.dumps({
            "ts": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            "level": level, "logger": "shoeshub", "message": message,
            "request_id": f"demo-{i:04d}", "method": method, "path": path,
            "status": status, "latency_ms": round(latency, 1),
        })})
    return events


def _metric_data(now: float) -> list[dict]:
    data: list[dict] = []
    for i in range(45):
        ts = datetime.fromtimestamp(now - (45 - i) * 60, tz=timezone.utc)
        frac = i / 45
        spike = 0.55 < frac < 0.72
        rps = 20 + 62 * frac
        values = {
            "RequestLatencyP99Ms": (round(40 + 230 * frac + (720 if spike else 0) + _jitter(i, -15, 25), 1), "Milliseconds"),
            "RequestsPerSecond": (round(rps + _jitter(i + 1, -5, 5), 1), "Count/Second"),
            "ErrorCount": (int(_jitter(i + 2, 4, 13)) if spike else 0, "Count"),
            "OrdersPlaced": (max(0, int(rps * 0.15) + int(_jitter(i + 4, -1, 3))), "Count"),
        }
        for name, (value, unit) in values.items():
            data.append({"MetricName": name, "Timestamp": ts, "Value": float(value),
                         "Unit": unit, "Dimensions": DIMS})
    return data


def _dashboard_body() -> dict:
    query = (f"SOURCE '{LOG_GROUP}' | fields @timestamp, request_id, path, status, latency_ms\n"
             "| filter level = 'ERROR'\n| sort @timestamp desc\n| limit 20")
    return {"widgets": [
        {"type": "metric", "x": 0, "y": 0, "width": 12, "height": 6, "properties": {
            "title": "p99 latency (ms)", "region": REGION, "stat": "Maximum", "period": 60,
            "metrics": [[NAMESPACE, "RequestLatencyP99Ms", "Environment", "qa"]]}},
        {"type": "metric", "x": 12, "y": 0, "width": 12, "height": 6, "properties": {
            "title": "Requests / sec", "region": REGION, "stat": "Average", "period": 60,
            "metrics": [[NAMESPACE, "RequestsPerSecond", "Environment", "qa"]]}},
        {"type": "metric", "x": 0, "y": 6, "width": 12, "height": 6, "properties": {
            "title": "Errors (5xx) & Orders placed", "region": REGION, "stat": "Sum", "period": 300,
            "metrics": [[NAMESPACE, "ErrorCount", "Environment", "qa"],
                        [NAMESPACE, "OrdersPlaced", "Environment", "qa"]]}},
        {"type": "log", "x": 12, "y": 6, "width": 12, "height": 6, "properties": {
            "title": "Recent errors (Logs Insights)", "region": REGION, "query": query, "view": "table"}},
    ]}


def seed() -> None:
    logs = boto3.client("logs", region_name=REGION)
    cw = boto3.client("cloudwatch", region_name=REGION)
    now = time.time()

    try:
        logs.create_log_group(logGroupName=LOG_GROUP)
    except logs.exceptions.ResourceAlreadyExistsException:
        pass
    logs.put_retention_policy(logGroupName=LOG_GROUP, retentionInDays=7)
    stream = "demo-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=stream)
    events = _log_events(now)
    logs.put_log_events(logGroupName=LOG_GROUP, logStreamName=stream, logEvents=events)
    logs.put_metric_filter(
        logGroupName=LOG_GROUP, filterName="error-count",
        filterPattern='{ $.level = "ERROR" }',
        metricTransformations=[{"metricName": "ErrorCountFromLogs",
                                "metricNamespace": NAMESPACE, "metricValue": "1", "defaultValue": 0}])

    data = _metric_data(now)
    for i in range(0, len(data), 150):
        cw.put_metric_data(Namespace=NAMESPACE, MetricData=data[i:i + 150])

    cw.put_metric_alarm(
        AlarmName=ALARM, AlarmDescription="ShoesHub QA demo: 5xx errors during load test",
        Namespace=NAMESPACE, MetricName="ErrorCount", Dimensions=DIMS,
        Statistic="Sum", Period=300, EvaluationPeriods=1, Threshold=0.0,
        ComparisonOperator="GreaterThanThreshold", TreatMissingData="notBreaching")
    cw.put_dashboard(DashboardName=DASHBOARD, DashboardBody=json.dumps(_dashboard_body()))

    print(f"seeded: {LOG_GROUP} ({len(events)} events), {len(data)} metric points, "
          f"alarm {ALARM}, dashboard {DASHBOARD}")
    print(f"open:   https://{REGION}.console.aws.amazon.com/cloudwatch/home"
          f"?region={REGION}#dashboards/dashboard/{DASHBOARD}")


def teardown() -> None:
    logs = boto3.client("logs", region_name=REGION)
    cw = boto3.client("cloudwatch", region_name=REGION)
    try:
        logs.delete_log_group(logGroupName=LOG_GROUP)
    except logs.exceptions.ResourceNotFoundException:
        pass
    cw.delete_alarms(AlarmNames=[ALARM])
    cw.delete_dashboards(DashboardNames=[DASHBOARD])
    print(f"deleted: {LOG_GROUP}, alarm {ALARM}, dashboard {DASHBOARD} "
          "(custom metrics stop billing once no new data is published)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed/remove ShoesHub CloudWatch demo data")
    parser.add_argument("--teardown", action="store_true",
                        help="delete the demo log group, alarm and dashboard")
    args = parser.parse_args()
    teardown() if args.teardown else seed()
