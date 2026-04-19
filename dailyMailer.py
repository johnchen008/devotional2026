import json
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo


CONFIG_FILE = Path(__file__).with_name("config.json")
STATE_FILE = Path(__file__).with_name("daily_devotion_state.json")
CHECK_INTERVAL_SECONDS = 60 * 60  # 1 hour


def load_json_file(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return data


def load_config() -> dict:
    config = load_json_file(CONFIG_FILE)

    required_top_keys = [
        "send_time",
        "timezone",
        "base_url",
        "smtp",
        "from_email",
        "to_emails",
    ]

    for key in required_top_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    smtp = config["smtp"]
    required_smtp_keys = ["host", "port", "username", "password", "use_starttls"]

    for key in required_smtp_keys:
        if key not in smtp:
            raise ValueError(f"Missing smtp config key: smtp.{key}")

    if not isinstance(config["to_emails"], list) or not config["to_emails"]:
        raise ValueError("to_emails must be a non-empty list")

    return config


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}

    try:
        return load_json_file(STATE_FILE)
    except Exception:
        return {}


def save_state(state: dict) -> None:
    temp_file = STATE_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    temp_file.replace(STATE_FILE)


def now_local(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def today_str(timezone_name: str) -> str:
    return now_local(timezone_name).date().isoformat()


def build_devotion_url(base_url: str, date_str: str) -> str:
    return f"{base_url.rstrip('/')}/{date_str}"


def scheduled_time_today(send_time: str, timezone_name: str) -> datetime:
    today = today_str(timezone_name)
    dt_str = f"{today} {send_time}"

    naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    return naive.replace(tzinfo=ZoneInfo(timezone_name))


def build_email(config: dict, date_str: str) -> EmailMessage:
    base_url = config["base_url"]
    from_email = config["from_email"]
    to_emails = config["to_emails"]

    devotion_url = build_devotion_url(base_url, date_str)

    subject = f"daily devotional{date_str}"
    body = (
        f"Today's devotion has been updated.\n\n"
        f"Date: {date_str}\n"
        f"Link: {devotion_url}\n\n"
        f"May you receive peace in the Lord today."
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body)

    return msg


def send_email(config: dict, date_str: str) -> None:
    smtp = config["smtp"]
    msg = build_email(config, date_str)

    host = smtp["host"]
    port = int(smtp["port"])
    username = smtp["username"]
    password = smtp["password"]
    use_starttls = bool(smtp["use_starttls"])

    context = ssl.create_default_context()

    if use_starttls:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(username, password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
            server.login(username, password)
            server.send_message(msg)


def check_and_send() -> None:
    try:
        config = load_config()
        state = load_state()

        timezone_name = config["timezone"]
        send_time = config["send_time"]

        today = today_str(timezone_name)
        last_sent = state.get("last_sent_date")

        current_time = now_local(timezone_name)
        scheduled_time = scheduled_time_today(send_time, timezone_name)

        if last_sent and last_sent >= today:
            print(
                f"[{current_time.isoformat()}] "
                f"Already sent today ({today})"
            )
            return

        if current_time < scheduled_time:
            print(
                f"[{current_time.isoformat()}] "
                f"Waiting for scheduled time {scheduled_time.isoformat()}"
            )
            return

        send_email(config, today)

        state["last_sent_date"] = today
        state["last_sent_at"] = current_time.isoformat()
        save_state(state)

        print(
            f"[{current_time.isoformat()}] "
            f"Sent devotion email for {today}"
        )

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)


def main() -> None:
    print("Starting devotion mailer.")
    print("Checks once on startup, then once every hour.")
    print(f"Config file: {CONFIG_FILE}")
    print(f"State file: {STATE_FILE}")

    check_and_send()

    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        check_and_send()


if __name__ == "__main__":
    main()