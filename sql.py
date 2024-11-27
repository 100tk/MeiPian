import sqlite3


def main():
    conn = sqlite3.connect("meipian.db")
    cur = conn.cursor()
    cur.execute(
        """--sql
                create table if not exists article
                (
                    id            integer primary key autoincrement  not null,
                    user_id       integer                            not null,
                    mask_id       text unique                        not null,
                    title         text                               not null,
                    cover_img_url text                           default null,
                    create_time   integer                            not null,
                    is_down       integer check ( is_down in (0, 1)) default 0,
                );
            """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
