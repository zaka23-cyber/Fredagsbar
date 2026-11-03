import os
from urllib.parse import quote

import httpx
import streamlit as st

API_URL = os.environ.get("API_URL", "http://127.0.0.1:5001")

st.title("Fredagsbarens events")

# Navnet huskes, mens brugeren klikker rundt.
if "name" not in st.session_state:
    st.session_state["name"] = ""

st.sidebar.text_input("Mit navn", key="name")
name = st.session_state["name"].strip()

# Vis beskeden efter en opdatering af siden.
if "message" in st.session_state:
    st.success(st.session_state.pop("message"))


def api_request(method, path, body=None):
    try:
        response = httpx.request(
            method,
            f"{API_URL}{path}",
            json=body,
            timeout=2,
        )
        response.raise_for_status()
        return response

    except httpx.ConnectError:
        st.error("Kan ikke kontakte API'en. Er den startet?")

    except httpx.TimeoutException:
        st.error("API'en svarer for langsomt. Prøv igen.")

    except httpx.HTTPStatusError as error:
        try:
            message = error.response.json().get(
                "error", "API'en afviste forespørgslen."
            )
        except (ValueError, AttributeError):
            message = "API'en returnerede et uventet fejlsvar."

        st.error(message)

    except httpx.RequestError:
        st.error("Der opstod en netværksfejl.")

    return None


def refresh(message):
    st.session_state["message"] = message
    st.rerun()


# Hent den aktuelle liste fra API'en.
response = api_request("GET", "/events")

if response is None:
    st.stop()

events = response.json()

st.subheader("Oversigt")

rows = [
    {
        "Titel": event["title"],
        "Dato": event["date"],
        "Antal tilmeldte": len(event["participants"]),
        "Ledige pladser": (
            event["capacity"] - len(event["participants"])
        ),
    }
    for event in events
]

if rows:
    st.dataframe(rows)
else:
    st.info("Der er ingen events endnu.")

st.subheader("Tilmeld og afmeld")

if events:
    events_by_id = {event["id"]: event for event in events}

    event_id = st.selectbox(
        "Vælg et event",
        options=list(events_by_id),
        format_func=lambda event_id: (
            f"{events_by_id[event_id]['title']} (#{event_id})"
        ),
    )

    event = events_by_id[event_id]
    participants = event["participants"]
    full = len(participants) >= event["capacity"]

    st.write(
        "Deltagere:",
        ", ".join(participants) if participants else "Ingen endnu",
    )

    if st.button("Tilmeld", disabled=full or not name):
        result = api_request(
            "POST",
            f"/events/{event_id}/signups",
            {"name": name},
        )

        if result is not None:
            refresh("Du er tilmeldt!")

    if st.button("Afmeld", disabled=not name):
        encoded_name = quote(name, safe="")

        result = api_request(
            "DELETE",
            f"/events/{event_id}/signups/{encoded_name}",
        )

        if result is not None:
            refresh("Du er afmeldt!")

    if full:
        st.info("Eventet er fuldt.")

st.subheader("Opret event")

with st.form("create_event"):
    title = st.text_input("Titel")
    date = st.date_input("Dato")
    capacity = st.number_input(
        "Antal pladser",
        min_value=1,
        value=5,
        step=1,
    )

    submitted = st.form_submit_button("Opret event")

if submitted:
    result = api_request(
        "POST",
        "/events",
        {
            "title": title,
            "date": date.isoformat(),
            "capacity": int(capacity),
        },
    )

    if result is not None:
        refresh("Eventet er oprettet!")