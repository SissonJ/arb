mkSeed = "SEED"
endpoint = "ENDPOINT"

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
    "tokenDecimals":{
        "token1": 6,
        "token2": 8,
    },
    "clientInfo": {
        "endpoint": endpoint,
        "chainID": "secret-4"
    },
    "logLocation": "shd-scrt-pair-log.csv",
    "fee": {
        "gas": 200001,
        "price": "050001uscrt",
    },
  }
}
