# Freelance Project Manager

A desktop application for managing freelance work: clients, projects,
milestones, tasks, time tracking, expenses, invoices, and reports.

**Course:** L3 Génie Logiciel — Programmation Orientée Objet en Python  
**Professor:** Prof. Patrick Mukala  
**Author:** Franck KIBWE KIETE

---

## Features

| Module        | Capabilities                                                                            |
| ------------- | --------------------------------------------------------------------------------------- |
| **Dashboard** | Active projects count, total income, pending invoices, weekly hours                     |
| **Clients**   | Add, edit, delete clients                                                               |
| **Projects**  | Create projects with budget, deadline, billing strategy; manage milestones and expenses |
| **Tasks**     | Create tasks (Development, Backend, Design, Writing); live timer; time entries          |
| **Invoices**  | Auto-generate invoices from billing strategy; mark as paid                              |
| **Reports**   | Income, Expense, Productivity, Profit reports                                           |

---

## Requirements

- Python 3.10 or later
- No external dependencies — uses only the Python standard library (`tkinter`, `sqlite3`, `abc`, `datetime`, `re`)

---

## Installation

```bash
# Clone or copy the project folder
cd FreelanceProjectManager

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

---

## Running the Application

```bash
# From the project root directory
python src/main.py
```

On **first launch** a setup wizard asks for your freelancer profile.
Subsequent launches go straight to the Dashboard.

The SQLite database file `freelance_manager.db` is created automatically in the project root.

---

## Project Structure

```
FreelanceProjectManager/
├── docs/
│   ├── description.md       # Detailed project specification
│   └── exam.md              # Exam requirements
├── src/
│   ├── main.py              # Entry point
│   ├── models/              # Domain entities (Person, Project, Task, …)
│   ├── database/            # Singleton DatabaseManager
│   ├── repositories/        # SQLite CRUD (one per entity)
│   ├── strategies/          # BillingStrategy hierarchy (Strategy pattern)
│   ├── factories/           # TaskFactory (Factory pattern)
│   ├── exceptions/          # Custom exception hierarchy
│   ├── services/            # Business logic layer
│   ├── gui/                 # Tkinter screens and widgets
│   └── utils/               # Validators and formatters
├── freelance_manager.db     # Auto-generated SQLite database
└── README.md
```

---

## OOP Concepts Demonstrated

| Concept                    | Location                                                                                                        |
| -------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Encapsulation**          | Private attrs (`__budget`, `__status`, …) + getters/setters with validation in every model                      |
| **Inheritance (3 levels)** | `Person → Freelancer → SeniorFreelancer` and `Task → DevelopmentTask → BackendDevelopmentTask`                  |
| **Abstraction (ABC)**      | `Person`, `Task`, `BillingStrategy` — each has ≥ 2 `@abstractmethod` methods                                    |
| **Polymorphism**           | `task.calculate_cost(hourly_rate)` and `strategy.calculate_invoice(project)` — different behaviour per subclass |

---

## Design Patterns

| Pattern       | Class                                                                       | Purpose                                                   |
| ------------- | --------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Singleton** | `DatabaseManager`                                                           | One SQLite connection for the app lifetime                |
| **Strategy**  | `BillingStrategy` → `HourlyBilling`, `FixedPriceBilling`, `RetainerBilling` | Project delegates invoice calculation to its strategy     |
| **Composite** | `Project → Milestone → Task`                                                | Progress propagates upward through the tree               |
| **Factory**   | `TaskFactory`                                                               | Creates the correct Task subclass from a string type name |

---

## Exception Handling

All service methods use `try / except / else / finally` blocks.  
Custom exceptions:

```
ApplicationException
├── BudgetExceededException
├── DeadlinePassedException
├── InvalidTaskException
├── InvoiceAlreadyPaidException
├── ClientNotFoundException
├── InvalidBillingStrategyException
├── ProfileNotFoundException
└── DuplicateInvoiceException
```

---

## Code Style

- **PEP 8** compliant
- `CamelCase` for classes, `snake_case` for functions and variables, `UPPER_CASE` for constants
- Google-style docstrings on all public classes and methods
