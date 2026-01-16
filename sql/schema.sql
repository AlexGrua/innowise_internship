BEGIN;

    CREATE TABLE IF NOT EXISTS rooms2 (

        id  BIGINT PRIMARY KEY,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS students2 (
        id BIGINT PRIMARY KEY,
        name TEXT NOT NULL,
        birthday DATE NOT NULL,
        sex CHAR(1) NOT NULL CHECK (sex IN ('M', 'F')),
        room_id BIGINT NOT NULL REFERENCES rooms2(id) ON DELETE RESTRICT

    );

COMMIT;
