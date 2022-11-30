## Schedule OGU

Bot that runs on Telegram.

## Self Host?

You need to set the environment variables for the bot to work. You can find the tokens and links for the token in `.env.example` file, and do change the name of file to `.env`.

---

In case you don't have [`Xvfb`](https://en.wikipedia.org/wiki/Xvfb) installed run the following command to install it:

```bash
sudo apt update
```
```bash
sudo apt-get install xvfb
```

---

Now you need to install dependencies, to do that run the following command, make sure you have [`python`](https://www.python.org/) version `3.10.0+` installed:

```bash
poetry install
```

---

After all that you can run the bot with the following command:

```bash
python3 starter.py polling
```
