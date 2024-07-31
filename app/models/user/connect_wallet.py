from pydantic import BaseModel

class ProofDomain(BaseModel):
    lengthBytes: int
    value: str

class Proof(BaseModel):
    timestamp: int
    domain: ProofDomain
    signature: str
    payload: str

class ConnectWalletRequest(BaseModel):
    address: str
    state_init: str
    network: str
    proof: Proof

class PayloadResponse(BaseModel):
    payload: str