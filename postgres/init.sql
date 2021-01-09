create user grassroot with password 'grassroot';
create schema if not exists grassroot authorization grassroot;

create table if not exists grassroot.groups (
    id serial PRIMARY KEY,
    group_name varchar(256),
    description text,
    creator_id bigint,
    longitude double precision,
    latitude double precision,
    creation_date timestamp NOT NULL
);

create table if not exists grassroot.group_admins (
    id serial PRIMARY KEY,
    admin_id bigint,
    group_id bigint,
    token varchar(256),
    CONSTRAINT fk_group
        FOREIGN KEY(group_id)
            REFERENCES grassroot.groups(id)
            ON DELETE CASCADE
);

grant all privileges on all tables in schema grassroot to grassroot;
