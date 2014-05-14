create table book(
timestamp_recorder timestamp primary key not null,
bids double precision[][],
asks double precision[][],
recorder_pid smallint default null,
recorder_version varchar(5) default null,
recorder_host_id varchar(5) default null
);
