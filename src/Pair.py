from utils_async import generateTxEncryptionKeysAsync
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient


class Pair:
    pair_addr: str
    pair_hash: str
    token0_addr: str
    token0_hash: str
    token1_addr: str
    token1_hash: str
    query: dict
    dex: str

    def __init__(self, info, code_hash, dex):
        if(dex == "sienna"):
            self.pair_addr = info["contract"]["address"]
            self.pair_hash = info["contract"]["code_hash"]
            self.token0_addr = info["pair"]["token_0"]["custom_token"]["contract_addr"]
            self.token0_hash = info["pair"]["token_0"]["custom_token"]["token_code_hash"]
            self.token1_addr = info["pair"]["token_1"]["custom_token"]["contract_addr"]
            self.token1_hash = info["pair"]["token_1"]["custom_token"]["token_code_hash"]
            self.query = "pair_info"
        if(dex == "sswap"):
            self.pair_addr = info["contract_addr"]
            self.pair_hash = code_hash
            self.token0_addr = info["asset_infos"][0]["token"]["contract_addr"]
            self.token0_hash = info["asset_infos"][0]["token"]["token_code_hash"]
            self.token1_addr = info["asset_infos"][1]["token"]["contract_addr"]
            self.token1_hash = info["asset_infos"][1]["token"]["token_code_hash"]
            self.query = { "pool": {} }
        self.dex = dex

    async def query_pair(self, client: AsyncLCDClient):
        nonceDict, keyDict = await generateTxEncryptionKeysAsync(client)
        return await client.wasm.contract_query(
            self.pair_addr,
            self.query,
            self.pair_hash,
            nonceDict["first"],
            keyDict["first"]
        )

    