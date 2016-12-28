drop table if exists shorties;
create table shorties (
  id integer primary key autoincrement,
  key text,
  url text,
  url_hash text,
  owner text
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  fullname text,
  email text,
  username text,
  password text,
  verified integer
);

insert into users (fullname, email, username, password, verified)
  values ("geoff golliher", "ggolliher@katch.com", "geoff.golliher",
  "e07f8c4ab682212744526982f0f08d336e1c9041", "1");
