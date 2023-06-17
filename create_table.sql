CREATE TABLE IF NOT EXISTS Client(
  id SERIAL PRIMARY KEY,
  first_name VARCHAR (30) NOT NULL,
  last_name VARCHAR (30) NOT NULL,
  email VARCHAR (30) NOT NULL UNIQUE CONSTRAINT check_email CHECK (email like '%@%')
);

CREATE TABLE IF NOT EXISTS Phone(
  id SERIAL PRIMARY KEY,
  number_phone INTEGER UNIQUE NOT NULL,
  client_id INTEGER REFERENCES Client(id) not null
);