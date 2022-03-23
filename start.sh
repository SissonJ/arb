#!/bin/bash
echo "Starting bots"

python ./src/arb_bot_2p.py sscrt-shd-config >> ./logs/sscrt-shd.log &
python ./src/arb_bot_2p.py sscrt-sienna-config >> ./logs/sscrt-sienna.log &
python ./src/arb_bot_2p.py sscrt-seth-config >> ./logs/sscrt-seth.log &
