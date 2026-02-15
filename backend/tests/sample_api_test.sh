#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "Creating passenger"
curl -s -X POST "$BASE_URL/passengers/request_ride" \
  -H 'Content-Type: application/json' \
  -d '{"pickup_lat":12.97,"pickup_lng":77.59,"drop_lat":13.01,"drop_lng":77.63,"luggage_count":1,"detour_tolerance":0.25}'
echo

echo "Running pool"
curl -s -X POST "$BASE_URL/pool/run"
echo

echo "Fetch ride 1"
curl -s "$BASE_URL/ride/1"
echo
