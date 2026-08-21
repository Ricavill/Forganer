import sys

import httpx

DEFAULT_BASE_URL = "http://localhost:8000"


def signup(client: httpx.Client, name: str, last_name: str, email: str, password: str) -> str:
    response = client.post(
        "/users/signup",
        json={"name": name, "last_name": last_name, "email": email, "password": password},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def login(client: httpx.Client, email: str, password: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": password})
    response.raise_for_status()
    return response.json()["access_token"]


def chat(client: httpx.Client, token: str, message: str) -> str:
    response = client.post(
        "/bot-agent/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()["reply"]


def _error_detail(exc: httpx.HTTPStatusError) -> str:
    try:
        return str(exc.response.json().get("detail", exc.response.text))
    except ValueError:
        return exc.response.text


def _authenticate(client: httpx.Client) -> str:
    while True:
        choice = input("1) Log in  2) Sign up  > ").strip()
        try:
            if choice == "1":
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                return login(client, email, password)
            if choice == "2":
                name = input("First name: ").strip()
                last_name = input("Last name: ").strip()
                email = input("Email: ").strip()
                password = input("Password: ").strip()
                return signup(client, name, last_name, email, password)
            print("Please enter 1 or 2.")
        except httpx.HTTPStatusError as exc:
            print(f"Error: {_error_detail(exc)}\n")
        except httpx.ConnectError:
            print(f"Could not reach the API at {client.base_url}. Is it running?\n")
            sys.exit(1)


def _chat_loop(client: httpx.Client, token: str) -> None:
    print("\nLogged in! Chat with your meetup organizer below. Type 'exit' to quit.\n")
    while True:
        message = input("You: ").strip()
        if message.lower() in {"exit", "quit"}:
            break
        if not message:
            continue
        try:
            reply = chat(client, token, message)
            print(f"Agent: {reply}\n")
        except httpx.HTTPStatusError as exc:
            print(f"Error: {_error_detail(exc)}\n")


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL
    with httpx.Client(base_url=base_url, timeout=60) as client:
        token = _authenticate(client)
        _chat_loop(client, token)


if __name__ == "__main__":
    main()
