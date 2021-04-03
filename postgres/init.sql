create user grassroot with password 'grassroot';
create schema if not exists grassroot authorization grassroot;

create table if not exists grassroot.groups (
    id serial PRIMARY KEY,
    group_name varchar(256) NOT NULL,
    description text,
    admin_id bigint NOT NULL,
    longitude double precision NOT NULL,
    latitude double precision NOT NULL,
    creation_date timestamp NOT NULL,
    UNIQUE(group_name)
);

create table if not exists grassroot.group_admins (
    id serial PRIMARY KEY,
    admin_id bigint NOT NULL,
    group_id bigint NOT NULL,
    group_name varchar(256) NOT NULL,
    token varchar(256) NULL,
    CONSTRAINT fk_group
        FOREIGN KEY(group_id)
            REFERENCES grassroot.groups(id)
            ON DELETE CASCADE
);

grant all privileges on all tables in schema grassroot to grassroot;
