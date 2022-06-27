from env import endpoint, testnet, mkSeed, mkSeed2, viewing_keys
#from env import mkSeed2 as mkSeed

sscrtAdresses = {
  "SSCRT_ADDRESS": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek",
  "SSCRT_KEY": viewing_keys["arb_v3"]["SSCRT_KEY"],
}

central_logs = {
  "arb_v2": {
    "inv": "../logs/arb_v2/inventory.csv",
    "log": "../logs/arb_v2/log.csv"
  },
  "arb_v3": {
    "inv": "../logs/arb_v3/inventory.csv",
    "log": "../logs/arb_v3/log.csv"
  }
}

chain_id = "secret-4"
sswap_query = { 'pool': {} }
sienna_query = 'pair_info'

config = {  
  "sscrt-shd-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1wwt7nh3zyzessk8c5d98lpfsw79vzpsnerj6d0", #SSWAP_SSCRT_SHD_PAIR
      "pair2": "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5", #SIENNA_SSCRT_SHD_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SHD_KEY"], #SHD_API_KEY
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
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-shd.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
  "sscrt-seth-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret14zv2fdsfwqzxqt7s2ushp4c4jr56ysyld5zcdf", #SSWAP_SSCRT_SETH_PAIR
      "pair2": "secret1m2lphcemd9f4faj9yvjyq876kfzdm0yvdartqa", #SIENNA_SSCRT_SETH_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SETH_KEY"], #SETH_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 18,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-seth-csv.csv",
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-seth.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
  "sscrt-swbtc-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret10x0k62eaal4q3t9c200qvmgftahxjqvdawn69c", #SSWAP_SSCRT_SWBTC_PAIR
      "pair2": "secret15cje8he9lazke3w7flqm2efse4p5fdjrjarv52", #SIENNA_SSCRT_SWBTC_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SWBTC_KEY"], #SWBTC_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 8,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-swbtc-csv.csv",
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-seth.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
  "sscrt-susdt-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1gyct75dc2pf20vtj3l86k2jxg79mffyh9ljve3", #SSWAP_SSCRT_SUSDT_PAIR
      "pair2": "secret1kdrjlga9qjazf0rv7ue8alyglepljlexwumv68", #SIENNA_SSCRT_SUSDT_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
    },
    "token1First": {
      "pair1": True,
      "pair2": True,
    },
    "tokenAddrs": {
      "token1": "secret1k0jntykt7e4g3y88ltc60czgjuqdy4c9e8fzek", #SSCRT_ADDRESS
      "token2": "secret18wpjn83dayu4meu6wnn29khfkwdxs7kyrz9c8f", #SUSDT_ADDRESS
    },
    "tokenKeys":{
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SUSDT_KEY"], #SUSDT_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 6,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-susdt-csv.csv",
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-susdt.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
  "sscrt-sxmr-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1rtgz90f7umulrg3a574p9n6d9hzcxmxqwdk9hj", #SSWAP_SXMR_SETH_PAIR
      "pair2": "secret10jr88entzckef4dxdk6pm8fpa09k87yzt0cwxd", #SIENNA_SXMR_SETH_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SXMR_KEY"], #SXMR_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 12,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-seth-csv.csv",
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-seth.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
  "sscrt-sienna-config": {
    "mkSeed": mkSeed,
    "pairAddrs": {
      "pair1": "secret1rxrg8mp4qm5703ccz26lgh8hx7gpnkujrn6qcr", #SSWAP_SSCRT_SIENNA_PAIR
      "pair2": "secret1guphvlle6wzjswda3ceuuu6m6ty36t6w5jn9rv", #SIENNA_SSCRT_SIENNA_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v3"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v3"]["SIENNA_KEY"], #SIENNA_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 18,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-sienna-csv.csv",
    "centralLogLoc": central_logs["arb_v3"]["log"],
    "outputLogLoc": "./../logs/sscrt-sienna.log",
    "fee": {
      "gas": 300000,
      "price": "6000uscrt",
    },
  },
}

configStdk = {
    #"sscrt-stdk-config": {
    "mkSeed": mkSeed2,
    "pairAddrs": {
      "pair1": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", #SIENNA_SSCRT_STKD_PAIR
      "pair2": "secret155ycxc247tmhwwzlzalakwrerde8mplhluhjct", #SIENNA_SSCRT_STKD_PAIR
    },
    "pairQueries": {
      "pair1": sswap_query, #SSWAP_QUERY
      "pair2": sienna_query, #SIENNA_QUERY
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
      "token1": viewing_keys["arb_v2"]["SSCRT_KEY"], #SSCRT_API_KEY
      "token2": viewing_keys["arb_v2"]["STKD_KEY"], #STKD_API_KEY
    },
    "tokenDecimals":{
      "token1": 6,
      "token2": 6,
    },
    "clientInfo": {
      "endpoint": endpoint,
      "chainID": chain_id
    },
    "logLocation": "./../logs/sscrt-stkd-csv.csv",
    "centralLogLoc": central_logs["arb_v2"]["log"],
    "outputLogLoc": "./../logs/sscrt-stkd.log",
    "fee": {
      "gas": 350001,
      "price": "87500uscrt",
    },
  #},
}
