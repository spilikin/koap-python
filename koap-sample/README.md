# Sample project fpr KOAP: Konnektor SOAP Library

Install on macOS
```
brew install pipx
pipx install poetry
```

Install on linux
```
sudo apt update
sudo apt install pipx
```

Run the sample
```

export KONNEKTOR_BASE_URL=https://...
export KONNEKTOR_MANDANT_ID=m1
export KONNEKTOR_CLIENT_SYSTEM_ID=c1
export KONNEKTOR_WORKPLACE_ID=w1
export KONNEKTOR_USER_ID=ABCDEF
export KONNEKTOR_AUTH_METHOD=basic
export KONNEKTOR_AUTH_BASIC_USERNAME=user1
export KONNEKTOR_AUTH_BASIC_PASSWORD=password
# use this on your own risk
# export KONNEKTOR_DANGER_VERIFY_TLS=false

# install dependencies
poetry install --no-root
# switch shell to poetry venv
poetry shell
# run python script
python sample.py
```