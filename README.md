# Nani Broken CI
Play a sound (NANIIIIIII!!!) when one of your CI pipeline failed.

## Usage

`poetry install`

Get a token for read_api (https://gitlab.example.com/profile/personal_access_tokens) and save it in a file named `token.txt`

Get your favorite sound and store it in a file named `nani.mp3`

```bash
python nani.py -p myproject1 -p myproject 2 -g mygroup1 https://gitlab.example.com
```

