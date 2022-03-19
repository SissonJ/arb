import asyncio
import base64
import json
from miscreant.aes.siv import SIV
from arb import LCDClient
from cryptography.hazmat.primitives import serialization
from typing import Optional

client = LCDClient('https://lcd.secret.llc', 'secret-4')
seed = client.utils.generate_new_seed()
privkey, pubkey = client.utils.generate_new_key_pair_from_seed(seed)

async def contract_query(
    contract_address: str, query: dict, height: Optional[int] = 0
):
    query_str = json.dumps(query, separators=(",", ":"))
    contract_code_hash = client.wasm.contract_hash(contract_address)
           
    encrypted = client.utils.encrypt(contract_code_hash, query_str)

    nonce = encrypted[0:32]
    encoded = base64.b64encode(bytes(encrypted)).hex()
    query_path = f"/wasm/contract/{contract_address}/query/{encoded}?encoding=hex&height={height}"

    query_result = await client._get(query_path)
    encoded_result = base64.b64decode(bytes(query_result["smart"], "utf-8"))
    decrypted = client.utils.decrypt(encoded_result, nonce)
    return json.loads(base64.b64decode(decrypted))

def encrypt(contract_code_hash: str, msg):
    seed = client.utils.generate_new_seed()
    privkey, pubkey = client.utils.generate_new_key_pair_from_seed(seed)
    nonce = client.utils.generate_new_seed()
    tx_encryption_key = client.utils.get_tx_encryption_key(nonce)

    siv = SIV(tx_encryption_key)

    plaintext = bytes(contract_code_hash, "utf-8") + bytes(msg, "utf-8")
    ciphertext = siv.seal(plaintext, [bytes()])

    key_dump = pubkey.public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )

    return nonce + [x for x in key_dump] + [x for x in ciphertext]

async def main():
    print(await contract_query('secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5', 'pair_info'))
asyncio.get_event_loop().run_until_complete(main())