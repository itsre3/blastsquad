import secrets
from datetime import datetime, timezone


def generate_wallet_challenge(wallet_address: str) -> str:
    nonce = secrets.token_urlsafe(32)
    timestamp = datetime.now(timezone.utc).isoformat()

    return (
        "BlastSquad wants you to sign in with your Solana account:\n"
        f"{wallet_address}\n\n"
        "Sign this message to prove wallet ownership.\n"
        "This request will not trigger a blockchain transaction.\n\n"
        f"Nonce: {nonce}\n"
        f"Issued At: {timestamp}"
    )