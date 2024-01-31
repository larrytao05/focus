Backend api for iOS productivity app (see https://github.com/larrytao05/focus-frontend)

##

API Overview

Database:

- Models include Users, Friend Requests, and Work sessions.
- One-to-many relationships between users & friend requests and between users & work sessions.
- Association table represents relationship between friends (two users).

API:

- Routes for:
- Getting one or all users
- Creating and deleting users
- Logging in
- Creating, deleting, or canceling work sessions
- Adding a friend (sending a friend request)
- Accepting a friend request
