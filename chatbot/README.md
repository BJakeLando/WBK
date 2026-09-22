# Website Assistant (chatbot)

A "Studio Assistant" chat bubble on every page of paintedbykarla.com, powered by Claude.

- Answers visitor questions using the **FAQs in the Django admin**, and only those FAQs.
- Sends anyone who wants to book, check a date, or get a quote to **Book Your Date** (`/accounts/add_venue/`).
- When it can't answer, it logs the question under **Questions to answer** and emails Karla. She types the answer, saves, and the assistant knows it from the next chat on.
- Saves every conversation under **Chat transcripts**, including API token usage.
- If anything is misconfigured it hides itself. It never breaks the site.

## One-time setup

**1. Anthropic API key**
1. Go to console.anthropic.com, open Settings → Workspaces, and create a workspace called `paintedbykarla`.
2. On its **Spend limits** tab, set a monthly cap (for example $25). You can't set limits on the Default workspace, which is why this gets its own.
3. Create an API key inside that workspace.

**2. Resend key (email alerts)**
1. Sign up at resend.com with the inbox that should receive alerts (`WatercolorsByKarla@hotmail.com`). Until a domain is verified, Resend only delivers to the address on the account.
2. Create an API key.
3. Optional, later: verify `paintedbykarla.com` in Resend (add its DNS records in GoDaddy). Then set `NOTIFY_FROM_EMAIL` to something like `Watercolors By Karla <hello@paintedbykarla.com>`.

**3. Railway → WBK web service → Variables**

| Variable | Required | Default / notes |
|---|---|---|
| `ANTHROPIC_API_KEY` | yes | The chat stays hidden without it |
| `RESEND_API_KEY` | yes, for email | Booking-form alerts and "question for you" alerts |
| `NOTIFY_TO_EMAIL` | no | `WatercolorsByKarla@hotmail.com` |
| `NOTIFY_FROM_EMAIL` | no | `Watercolors By Karla <onboarding@resend.dev>` |
| `CHATBOT_MODEL` | no | `claude-sonnet-5` |
| `CHATBOT_DAILY_MESSAGE_LIMIT` | no | `600` visitor messages per day, site-wide |
| `CHATBOT_ENABLED` | no | Set to `false` to hide the chat instantly (kill switch) |

**4. Deploy.** Run `python manage.py migrate` and `python manage.py collectstatic --noinput`. The Procfile already does both on Railway. `collectstatic` also needs to run locally if `staticfiles/` is still committed.

## How Karla trains the assistant

1. Log in at `/admin/` and open **Website Assistant → Questions to answer**.
2. Click a question, type the answer the way you'd tell a client, and click **Save**. It becomes an FAQ right away.
3. To change or add anything else, use **FAQs (what the assistant knows)**. To hide an FAQ without deleting it, untick "Assistant uses this".
4. Skim **Chat transcripts** now and then to see what people ask.

Put real details in the answers: prices, policies, timelines. The assistant is told never to invent anything that isn't in the FAQs, so a missing detail makes it say "I don't have that yet", not guess.

## Costs and guard rails

- Claude Sonnet 5 costs $2 per million input tokens and $10 per million output tokens. The FAQ prompt is cached, and cached reads cost 10% of the normal input price, so a typical conversation costs about 2–4¢.
- Per visitor: 800 characters per message, 30 messages per chat, 20 messages per 10 minutes, and 120 per day.
- Site-wide: 600 visitor messages per day. After that, visitors see a polite "email Karla or use the booking form" message and no API calls are made. That puts the worst case at roughly $3 a day.
- "Question for you" emails are capped at about 10 per day.
- Resend's free plan allows 3,000 emails a month and 100 a day.

To switch models, set `CHATBOT_MODEL`. For example, `claude-haiku-4-5-20251001` is half the price, but Anthropic lists its retirement as "not sooner than Oct 15, 2026". If a model rejects the `effort` setting, set `CHATBOT_EFFORT` to an empty value.

## Troubleshooting (check Railway's deploy logs)

- **No chat bubble:** `ANTHROPIC_API_KEY` isn't set, `CHATBOT_ENABLED=false`, or the log says `Chat widget hidden` (run collectstatic).
- **Bot says it's "having trouble":** look for `Claude API error HTTP 401` (bad key), `404` (model name), or `400` (unsupported setting).
- **No emails:** look for `Resend rejected email`. Usually the recipient isn't the Resend account's address, or the sender domain isn't verified yet.

## Files

| File | Purpose |
|---|---|
| `assistant.py` | Builds the prompt from the FAQs and calls Claude with plain `requests` (no new packages) |
| `views.py`, `urls.py` | `/chatbot/message/`, `/chatbot/history/`, `/chatbot/reset/` |
| `ratelimit.py`, `conf.py` | Limits and settings with defaults |
| `admin.py`, `models.py` | FAQs, Questions to answer, Chat transcripts |
| `templatetags/chatbot_tags.py` | `{% chatbot_widget %}`, used in `templates/base.html` |
| `static/chatbot/chat.js`, `chat.css` | The widget (no dependencies; replies are rendered without innerHTML) |
| `migrations/0002_seed_knowledge.py` | Starter FAQs taken from the site |
| `migrations/0003_quality_over_quantity.py` | Karla's pace: roughly 15–20 minutes per detailed portrait; she finishes the rest at home and mails them to the bride and groom |
| `../mysite/notifications.py` | Resend email helper, shared with the booking form |

Tests: `python manage.py test chatbot accounts`

Privacy: transcripts store what visitors type. IP addresses are stored only as keyed hashes, for rate limiting. Delete old transcripts in the admin (select them, then Delete).
