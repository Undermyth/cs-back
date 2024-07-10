create table logs(
    id int primary key,
    title varchar(200),
    filepath varchar(200),
    starttime date,
    endtime date,
    len int,
    abstract varchar(500)
);

-- logs, columns and articles does not share the same id
-- uptime is alias for update time. because time is a keyword

create table columns(
    id int primary key,
    title varchar(200),
    uptime date,
    abstract varchar(500),
    dirpath varchar(200)
);

create table articles(
    id int primary key,
    title varchar(200),
    uptime date,
    filepath varchar(200),
    abstract varchar(500),
    len int,
    columnid int,
    foreign key (columnid) references columns(id)
);
