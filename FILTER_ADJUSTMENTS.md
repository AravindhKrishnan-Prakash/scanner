# Filter Adjustments - April 2, 2026

## Problem Identified
System showing "NO TRADE" for all stocks because filters were too strict for current market conditions.

## Root Causes
1. **Volume Filter Too Strict**: Required 1.5x surge, but market showing 0.56x-1.22x
2. **ADX Too High**: Required 15, some good setups at 12-14
3. **Voting Threshold**: Required 3 votes, reduced to 2.5 for more signals
4. **VWAP Hard Filter**: Rejected immediately if price wrong side of VWAP
5. **Session Timing**: Blocked 11:30-13:30 and after 14:30 (too restrictive)

## Changes Made

### 1. Volume Filter (config/watchlist.json)
- **Before**: minimum_volume_ratio: 1.5
- **After**: minimum_volume_ratio: 1.0
- **Reason**: Market rarely shows 1.5x surge; 1.0x is more realistic

### 2. ADX Filter (config/watchlist.json)
- **Before**: minimum_adx: 15
- **After**: minimum_adx: 12
- **Reason**: Trends at 12-14 ADX can still be tradeable

### 3. Voting Threshold (decision_engine.py)
- **Before**: Need 3.0 votes for signal
- **After**: Need 2.5 votes for signal
- **Reason**: More lenient while still requiring majority confirmation

### 4. VWAP Check (decision_engine.py)
- **Before**: Hard rejection if price wrong side of VWAP
- **After**: Allow 0.5% tolerance, make it a warning not rejection
- **Reason**: Price can be slightly off VWAP and still valid

### 5. Session Timing (live_scanner.py)
- **Before**: Block 9:15-9:30, 11:30-13:30, after 14:30
- **After**: Block 9:15-9:25, 12:00-13:00, after 15:00
- **Reason**: Extended trading windows for more opportunities

### 6. Quality Thresholds (decision_engine.py)
- **Before**: min_score: 5.5, min_prob: 55%
- **After**: min_score: 5.0, min_prob: 50%
- **Reason**: Slightly lower bar for signal generation

## Expected Results
- **More signals**: 3-8 per day instead of 0
- **Still quality-focused**: All filters still active, just more realistic
- **Better for Indian markets**: Adjusted to actual market conditions

## Next Steps
1. Restart dashboard_server.py
2. Click "Scan Now" to test
3. Monitor during optimal windows (10:00-11:30 AM, 1:30-2:30 PM tomorrow)
4. Adjust further if needed based on signal quality
