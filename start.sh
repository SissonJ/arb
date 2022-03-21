#!/bin/bash
echo "Starting bots"

python arb_bot_2p.py sscrt-shd-config >> ./logs/sscrt-shd.log &
python arb_bot_2p.py sscrt-sienna-config >> ./logs/sscrt-sienna.log &
