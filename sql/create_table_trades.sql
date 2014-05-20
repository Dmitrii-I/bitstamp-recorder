create table trades(
timestamp_recorder timestamp primary key not null,
bitstamp_trade_id integer,
price double precision not null,
volume double precision not null,
recorder_pid smallint default null,
recorder_version varchar(5) default null,
recorder_host_id varchar(5) default null
);
