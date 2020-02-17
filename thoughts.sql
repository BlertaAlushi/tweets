create database thoughts;
use thoughts;

create table users (
id int auto_increment,
first_name varchar(45),
last_name varchar(45),
email varchar(45),
password varchar(60),
primary key(id)
);

create table thoughts (
id int auto_increment,
thought varchar(255),
user_id int,
primary key(id),
foreign key(user_id) references users(id) on delete cascade
);

create table likes(
id int auto_increment,
thought_id int,
user_id int,
primary key(id),
foreign key(user_id) references users(id) on delete cascade,
foreign key(thought_id) references thoughts(id) on delete cascade
);
