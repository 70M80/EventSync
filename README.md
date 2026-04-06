# EventSync - Group Date Picker

**A simple, no-signup web app to easily find the best common dates for vacations, weekends, or any group event.**

Inspired by Doodle and When2Meet, but designed specifically for selecting **date ranges** (perfect for planning holidays with friends).

## ✨ Features

- Create an event in seconds (vacation, trip, weekend, etc.)
- Share with friends using a simple **Event Code** + password
- Each participant selects their available **date ranges**
- **Real-time updates** — see changes instantly via WebSockets
- Clear visualization of **common availability** (intersection of all responses)
- No accounts, no emails, no registration required
- Each participant gets a personal **Access Code** to edit their dates anytime

## 🚀 How It Works

### Creating an Event
1. Enter event name, password, max number of responses, and your username
2. Receive an **Event Code** to share + your personal **Access Code**

### Participating
- **New participant**: Enters Event Code + password + their name → receives their own Access Code
- **Returning participant**: Enters only their **Access Code** to view and edit their date ranges

All changes are instantly visible to everyone currently viewing the event.

## 🛠 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Vue 3
- **Real-time**: WebSockets (native FastAPI)
- **Database**: PostgreSQL + SQLAlchemy 2.0 + Alembic
- **Validation**: Pydantic v2

## 🔑 Key Concepts
- **Event Code**: Public identifier used to join the event
- **Event Password**: Protection when joining
- **Access Code**: Private code for each participant to edit their responses (generated automatically)
- **Intersection**: Automatically calculated common date ranges where everyone (or most people) can go
