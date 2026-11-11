# 🔐 The Intern's Token (Experienced — Web Exploitation / JWT)

## Story

> You're interning on the security team at **Globex Dynamics** (a fictional
> company, invented for this exercise). On your first day, the portal hands
> you a standard employee session token and a friendly warning from a
> teammate: *"Heads up — someone captured a token just like yours during
> last month's internal pentest. IT swears the tokens are safe. Prove them
> wrong."*
>
> Your goal: escalate from `employee` to `admin` and read the flag served
> at `/admin`.

## Target

- Local/Docker: `http://localhost:5000/`
- Visiting `/` issues you a standard-role JWT (as a cookie and shown on
  the page).
- `/admin` requires `role: admin` inside the JWT payload.

## Flag format

`GDG{...}`

## Hint Ladder

**Hint 1 (free / low cost):**
> JWTs have three dot-separated parts: header, payload, signature. The
> first two are just Base64url — not encrypted. Decode your token (e.g. at
> jwt.io or with `pyjwt`) and look at what's inside the payload.

**Hint 2 (medium cost):**
> You can edit the payload all you want, but the server checks the
> signature before trusting it. The signature here uses `HS256`, which
> means it's signed (and verified) with a single shared secret — not a
> public/private keypair. If that secret is weak or guessable, you can
> recompute a valid signature yourself.

**Hint 3 (high cost, near-full spoiler):**
> The secret is a short, real-word-based string that wouldn't survive five
> minutes against a small wordlist (think: company name + a recent year).
> Tools like `jwt_tool`, `hashcat` (mode 16500), or a 10-line Python script
> using `PyJWT`'s `decode(token, candidate, algorithms=["HS256"])` in a
> loop over a short candidate list will crack it. Once cracked, re-sign a
> payload with `"role": "admin"` using that secret.

## Difficulty notes for organizers

This challenge requires understanding JWT structure, knowing that HS256
tokens are symmetric (forgeable once you know the secret), and basic
scripting or tool usage to brute-force a weak secret. It's a step up from
"read the source" challenges but doesn't require any memory corruption,
binary analysis, or advanced tooling — appropriate for players with some
prior CTF/web security experience.
