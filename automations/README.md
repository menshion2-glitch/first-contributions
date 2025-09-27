# Instagram DM Responder Automation

This folder contains a sample Python script that automates replies to
Instagram Direct Messages (DMs) based on the content of the incoming
message. The automation uses the [instagrapi](https://github.com/adw0rd/instagrapi)
client to interact with Instagram.

## Requirements

* Python 3.9+
* The [`instagrapi`](https://pypi.org/project/instagrapi/) package

Install the dependency with:

```bash
pip install instagrapi
```

## Usage

1. Set up environment variables with your Instagram credentials and
   optional configuration:

   ```bash
   export IG_USERNAME="your_username"
   export IG_PASSWORD="your_password"
   export IG_DEFAULT_RESPONSE="Thanks for reaching out! We'll get back to you soon."
   export IG_POLL_INTERVAL="30"  # optional, defaults to 30 seconds
   export IG_SESSION_PATH="/path/to/session.json"  # optional, for persistent login
   ```

2. (Optional) Edit the responder rules defined in
   [`instagram_dm_responder.py`](./instagram_dm_responder.py) to
   customize the keyword-based auto replies.

3. Run the script:

   ```bash
   python automations/instagram_dm_responder.py
   ```

The script polls your inbox every ``IG_POLL_INTERVAL`` seconds and sends a
reply when a keyword rule matches the most recent message from a contact.
If no rule matches, the `IG_DEFAULT_RESPONSE` value (when provided) is sent.

> **Important:** Always follow Instagram's platform policies when using
> automation. Sending unsolicited or excessive automated messages can lead
> to account restrictions.
