# Frontend plan (MVP)

## Tech stack
- Vue 3 + TypeScript (Vite)
- Pinia for state management
- Vue Router
- Axios for HTTP

## Pages / components
### Views
- `TicketsView` (`/tickets`)
  - Displays ticket list
  - Button to create a new ticket
  - Each row shows title, status, and formatted timestamp
  - Clicking a row opens ticket details (with e.g. modal)

### Components
- `TicketList` (list + empty state)
- `TicketRow` (title/status/date + click handler)
- ``TicketDetailModal` (title/description/status + status update control)
- `TicketForm` (create ticket form; modal or inline expand)

## API communication
- The frontend communicates with the backend REST API via Axios, targeting `http://127.0.0.1:8000`.
- Use a dedicated service module `services/ticketService.ts` for all backend communication:
  - `GET /tickets` -> returns `Ticket[]`
  - `POST /tickets` -> creates a ticket (request body as specified by the API)
  - `PATCH /tickets/{id}` -> updates ticket status (request body as specified by the API), returns 204 on success


## State management (Pinia)
- `useTicketStore`
  - State:
    - `tickets: Ticket[]`
    - `loading: boolean`
    - `errorMessage: string | null`
  - Actions:
    - `fetchTickets()`
    - `createTicket(payload)`
    - `updateTicketStatus(id, status)`
- After successful mutations (`POST` / `PATCH`), update the Pinia store state accordingly
  - POST: append the created ticket to `tickets`
  - PATCH (204): update the ticket status in `tickets` based on the request payload

## Loading states, errors, and validation
- Loading:
  - Whenever communicating with the server asynchronously, indicate progress (with e.g. spinner/disabled UI)
- Errors:
  - If the user can act on it (e.g., 409 title conflict; 422 validation fallback), display the returned error message near the relevant UI (form field / banner)
  - If the user cannot act on it (unexpected errors), show a generic “Something went wrong” message and provide a retry option
- Form validation:
  - Validate required fields (`title`, `description`) and disable submit until valid

## Project structure (simple MVP)
- `src/services/ticketService.ts` (HTTP calls + JSON parsing)
- `src/stores/ticketStore.ts` (Pinia store)
- `src/views/TicketsView.vue` (main page)
- `src/components/` (TicketForm, TicketDetailModal, TicketList, TicketRow)
- `src/models/ticket.ts` (TypeScript interfaces/types, e.g. `Ticket`, `TicketStatus`, DTOs)
- `src/router/index.ts` (routes: `/tickets`, redirect `/` -> `/tickets`)
