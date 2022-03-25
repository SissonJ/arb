#!/bin/bash
echo "Starting bots"

cd ./src

python arb_bot_2p.py sscrt-shd-config >> ./logs/sscrt-shd.log &
python arb_bot_2p.py sscrt-sienna-config >> ./logs/sscrt-sienna.log &
python arb_bot_2p.py sscrt-seth-config >> ./logs/sscrt-seth.log &
python arb_bot_2p.py sscrt-swbtc-config >> ./logs/sscrt-swbtc.log &
python arb_bot_2p.py sscrt-sxmr-config >> ./logs/sscrt-sxmr.log &
