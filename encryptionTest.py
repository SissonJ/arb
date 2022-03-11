import asyncio
import base64
import json
from miscreant.aes.siv import SIV
from secret_sdk.client.lcd import LCDClient
from secret_sdk.key.mnemonic import MnemonicKey
from secret_sdk.core.wasm import MsgExecuteContract
from cryptography.hazmat.primitives import hashes, serialization
from typing import Optional
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

hkdf_salt = bytes(
  [
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x02,
    0x4B,
    0xEA,
    0xD8,
    0xDF,
    0x69,
    0x99,
    0x08,
    0x52,
    0xC2,
    0x02,
    0xDB,
    0x0E,
    0x00,
    0x97,
    0xC1,
    0xA1,
    0x2E,
    0xA6,
    0x37,
    0xD7,
    0xE9,
    0x6D,
  ]
)

mkSeed = "easy oxygen bone search trophy soccer video float tiny rack fragile cactus uphold acoustic carbon warm hand pilot topic session because seed magnet domain"
mk = MnemonicKey(mnemonic=mkSeed)
client = LCDClient('https://lcd.secret.llc', 'secret-4')
wallet = client.wallet(mk)
privkey = X25519PrivateKey.from_private_bytes(mk.private_key)
pubkey =  privkey.public_key()
consensusIoPubKey = X25519PublicKey.from_public_bytes(client.utils.get_consensus_io_pubkey())
tx_encryption_ikm = privkey.exchange(consensusIoPubKey)

SHD_ADDRESS = 'secret1qfql357amn448duf5gvp9gr48sxx9tsnhupu3d'
SHD_CONTRACT_HASH = client.wasm.contract_hash(SHD_ADDRESS)

SIENNA_SSCRT_SHD_PAIR = "secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5"

def getTxEcryptionKey(nonce):
  global tx_encryption_ikm

  masterSecret = bytes([x for x in tx_encryption_ikm] + nonce)
  tx_encryption_key = HKDF(
    algorithm=hashes.SHA256(), length=32, salt=hkdf_salt, info=b"", backend=None
  ).derive(masterSecret)

  print(tx_encryption_key)
  print(client.utils.get_tx_encryption_key(nonce))

  return tx_encryption_key

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

def encrypt(msg):
  global pubkey, SHD_CONTRACT_HASH

  nonce = client.utils.generate_new_seed()
  tx_encryption_key = getTxEcryptionKey(nonce)

  siv = SIV(tx_encryption_key)

  plaintext = bytes(SHD_CONTRACT_HASH, "utf-8") + bytes(msg, "utf-8")
  ciphertext = siv.seal(plaintext, [bytes()])

  key_dump = pubkey.public_bytes(
    encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
  )

  encrypted = nonce + [x for x in key_dump] + [x for x in ciphertext]
  encoded = base64.b64encode(bytes(encrypted)).hex()
  return encoded, encrypted[0:32]

async def main():
    print(await contract_query('secret1drm0dwvewjyy0rhrrw485q4f5dnfm6j25zgfe5', 'pair_info'))
#asyncio.get_event_loop().run_until_complete(main())

def main2():
  global SIENNA_SSCRT_SHD_PAIR, SHD_ADDRESS

  msgSienna = json.dumps({"swap":{"to":None,"expected_return":"0"}})
  encryptedMsgSienna = str( base64.b64encode(msgSienna.encode("utf-8")), "utf-8")
  handleMsgSienna = { "send": {"recipient": SIENNA_SSCRT_SHD_PAIR, "amount": "1000", "msg": encryptedMsgSienna }}
  handleMsgSiennaStr = json.dumps(handleMsgSienna, separators=(",", ":"))
  encryptedHandleMsgSienna, nonce = encrypt(handleMsgSiennaStr)
  #print(type(encryptedHandleMsgSienna))
  msgExecute = MsgExecuteContract(mk.acc_address, SHD_ADDRESS, encryptedHandleMsgSienna,[])
  tx = wallet.create_and_sign_tx([msgExecute])
  #print(tx.to_data())
  #res = client.tx.broadcast(tx)
  #decryptres = client.tx.decrypt_txs_response(res)
  #print(res)
  #print(decryptres)

main2()
