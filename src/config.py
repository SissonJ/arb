from env import endpoint, testnet, mkSeed
#from env import mkSeed2 as mkSeed

sscrtAdresses = {
  "SSCRT_ADDRESS": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek",
  "SSCRT_KEY": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU="
}

config = {  
  "sscrt-shd-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0", #SSWAP_SSCRT_SHD_PAIR
      "pair2": "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5", #SIENNA_SSCRT_SHD_PAIR
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": False,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d", #SHD_ADDRESS
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "api_key_dbViT6Q9NycWc04tJ8DaylmO1BWGcWz8rJixY3/ZQnY=", #SHD_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 8,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-shd-csv.csv",
    "fee": {
      "gas": 200001,
      "price": "050001uscrt",
    },
  },
  "sscrt-seth-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret14zv2fdsfwqzxqt7s2ushp4c4jr56ysyld5zcdf", #SSWAP_SSCRT_SETH_PAIR
      "pair2": "secret1m2lphcemd9f4faj9yvjyq876kfzdm0yvdartqa", #SIENNA_SSCRT_SETH_PAIR
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": True,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret1wuzzjsdhthpvuyeeyhfq2ftsn3mvwf9rxy6ykw", #SETH_ADDRESS
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "api_key_tfA3AUYa/EH5mk0cIv7WqmYlz4VZktu7HiBUXW1HbrU=", #SETH_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 18,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-seth-csv.csv",
    "fee": {
      "gas": 200001,
      "price": "050001uscrt",
    },
  },
  "sscrt-swbtc-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret10x0k62eaal4q3t9c200qvmgftahxjqvdawn69c", #SSWAP_SSCRT_SWBTC_PAIR
      "pair2": "secret15cje8he9lazke3w7flqm2efse4p5fdjrjarv52", #SIENNA_SSCRT_SWBTC_PAIR
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": True,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret1g7jfnxmxkjgqdts9wlmn238mrzxz5r92zwqv4a", #SWBTC_ADDRESS
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "api_key_c5NVcP5dQ1E5sZF6oJh75uYFs/FiZJKBgY8jIpXrZ+s=", #SWBTC_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 8,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-swbtc-csv.csv",
    "fee": {
      "gas": 200001,
      "price": "050001uscrt",
    },
  },
}

configStdk = {
    #"sscrt-stdk-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", #SIENNA_SSCRT_STKD_PAIR
      "pair2": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", #STKD_CONTRACT
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": True,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret1k6u0cy4feepm6pehnz804zmwakuwdapm69tuc4", #STKD_CONTRACT
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "a24cefc2fd7de8811c4dcd6964f351d4d9f999c3ec4d7543546543c1258c63d2", #STKD_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 6,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-stkd-csv.csv",
    "fee": {
      "gas": 300001,
      "price": "075000uscrt",
    },
  #},
}

"""
  "sscrt-sxmr-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1rtgz90f7umulrg3a574p9n6d9hzcxmxqwdk9hj", #SSWAP_SXMR_SETH_PAIR
      "pair2": "secret10jr88entzckef4dxdk6pm8fpa09k87yzt0cwxd", #SIENNA_SXMR_SETH_PAIR
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": False,
      "pair2": False,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret19ungtd2c7srftqdwgq0dspwvrw63dhu79qxv88", #SXMR_ADDRESS
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "api_key_tXggdXqRd4Bq06tQdLrq3EDeQJCdKVm56ciGjusX6ik=", #SXMR_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 12,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-seth-csv.csv",
    "fee": {
      "gas": 200001,
      "price": "050001uscrt",
    },
  },"""

"""
  "sscrt-sienna-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1rxrg8mp4qm5703ccz26lgh8hx7gpnkujrn6qcr", #SSWAP_SSCRT_SIENNA_PAIR
      "pair2": "secret1guphvlle6wzjswda3ceuuu6m6ty36t6w5jn9rv", #SIENNA_SSCRT_SIENNA_PAIR
    },
    "pairQueries": {
      "pair1": { 'pool': {} }, #SSWAP_QUERY
      "pair2": 'pair_info', #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": False,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret1rgm2m5t530tdzyd99775n6vzumxa5luxcllml4", #SIENNA_ADDRESS
    },
    "tokenKeys":{
      "token1": "api_key_3wPSbtuDquKHhFw1zSFILDXnQnsGz2TuISVAnlmUgYU=", #SSCRT_API_KEY
      "token2": "api_key_IiGUpxiB9+hry8VNpAx+6C9x72Tz1KEkhvAWtpLQUUU=", #SIENNA_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 18,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": "secret-4"
    },
    "logLocation": "./../logs/sscrt-sienna-csv.csv",
    "fee": {
      "gas": 200001,
      "price": "050001uscrt",
    },
  },"""
