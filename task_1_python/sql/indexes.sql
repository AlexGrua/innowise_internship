BEGIN;

CREATE INDEX IF NOT EXISTS idx_students_room_id
    ON students2 (room_id);
CREATE INDEX IF NOT EXISTS idx_students_room_id_sex
    ON students2 (room_id, sex);
CREATE INDEX IF NOT EXISTS idx_students_room_id_birthday
    ON students2 (room_id, birthday);


COMMIT;