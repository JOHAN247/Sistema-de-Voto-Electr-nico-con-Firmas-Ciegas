
PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL, -- Código de 6 dígitos único
    status TEXT DEFAULT 'PENDING', -- PENDING, ACTIVE, FINISHED
    options TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS election_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    has_voted INTEGER DEFAULT 0, -- 0 = No ha votado, 1 = Ya se le firmó su token
    FOREIGN KEY (election_id) REFERENCES elections(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(election_id, user_id) -- Un usuario solo se registra una vez por elección
);


CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL,
    option_selected TEXT NOT NULL, -- El candidato o respuesta elegida
    signature TEXT UNIQUE NOT NULL, -- La firma descegada que valida que este voto es legal
    FOREIGN KEY (election_id) REFERENCES elections(id)
);