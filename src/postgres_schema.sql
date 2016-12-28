drop table if exists shorties;
create table shorties (
  id serial primary key,
  key text,
  url text,
  url_hash text,
  owner text
);

drop table if exists users;
create table users (
  id serial primary key,
  fullname text,
  username text,
  password text
);

insert into users (fullname, username, password)
  values ('geoff golliher', 'geoff.golliher',
  'e07f8c4ab682212744526982f0f08d336e1c9041');
