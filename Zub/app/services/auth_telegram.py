import hmac
import hashlib
from typing import Dict, Any
from app.config import settings

def verify_telegram_login(data: Dict[str, Any]) -> bool:
    """Verify Telegram Login Widget payload."""
    if "hash" not in data:
        return False

    received_hash = data["hash"]
    check_dict = {k: v for k, v in data.items() if k != "hash"}
    data_check_string = "\n".join(f"{k}={check_dict[k]}" for k in sorted(check_dict.keys()))

    if not settings.TELEGRAM_BOT_TOKEN:
        return False

    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_hash, received_hash)
