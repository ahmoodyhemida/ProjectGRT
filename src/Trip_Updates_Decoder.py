import os
import sqlite3
from pathlib import Path
from google.transit import gtfs_realtime_pb2

TRIP_UPDATES_FOLDER = Path("GRT_GTFS/Trip_Updates")
db_filepath = 'Trip_Updates_Static_Feed.db'

def process_full_trip_updates(pb_filepath, db_filepath):
    filename = os.path.basename(pb_filepath)
    fetched_at = filename.replace('trip_updates_', '').replace('.pb', '')
    fetched_at = fetched_at[:-7]

    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS feed_header (
            fetched_at TEXT,
            gtfs_realtime_version TEXT,
            incrementality INTEGER,
            timestamp INTEGER,
            feed_version TEXT
        );

        CREATE TABLE IF NOT EXISTS trip_update (
            trip_update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            entity_id TEXT,
            timestamp INTEGER,
            delay INTEGER,

            trip_id TEXT,
            route_id TEXT,
            direction_id INTEGER,
            start_time TEXT,
            start_date TEXT,
            schedule_relationship INTEGER,

            mod_modifications_id TEXT,
            mod_affected_trip_id TEXT,
            mod_start_time TEXT,
            mod_start_date TEXT,

            vehicle_id TEXT,
            vehicle_label TEXT,
            vehicle_license_plate TEXT,
            vehicle_wheelchair_accessible INTEGER,

            prop_trip_id TEXT,
            prop_start_date TEXT,
            prop_start_time TEXT,
            prop_shape_id TEXT,
            prop_trip_headsign TEXT,
            prop_trip_short_name TEXT,
            
            UNIQUE (entity_id, fetched_at)
        );

        CREATE TABLE IF NOT EXISTS stop_time_update (
            stop_time_update_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT,
            trip_entity_id TEXT,

            stop_sequence INTEGER,
            stop_id TEXT,

            arrival_delay INTEGER,
            arrival_time INTEGER,
            arrival_uncertainty INTEGER,
            arrival_scheduled_time INTEGER,

            departure_delay INTEGER,
            departure_time INTEGER,
            departure_uncertainty INTEGER,
            departure_scheduled_time INTEGER,

            departure_occupancy_status INTEGER,
            schedule_relationship INTEGER,

            prop_assigned_stop_id TEXT,
            prop_stop_headsign TEXT,
            prop_pickup_type INTEGER,
            prop_drop_off_type INTEGER,

            FOREIGN KEY(trip_entity_id, fetched_at) REFERENCES trip_update(entity_id, fetched_at)
        );
    ''')

    feed = gtfs_realtime_pb2.FeedMessage()
    with open(pb_filepath, 'rb') as f:
        feed.ParseFromString(f.read())

    cursor.execute('''
        INSERT INTO feed_header (fetched_at, gtfs_realtime_version, incrementality, timestamp, feed_version)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        fetched_at,
        feed.header.gtfs_realtime_version,
        feed.header.incrementality,
        feed.header.timestamp if feed.header.HasField('timestamp') else None,
        feed.header.feed_version if feed.header.HasField('feed_version') else None
    ))

    for entity in feed.entity:
        if not entity.HasField('trip_update'):
            continue

        tu = entity.trip_update
        trip = tu.trip if tu.HasField('trip') else None
        mod = trip.modified_trip if trip and trip.HasField('modified_trip') else None
        veh = tu.vehicle if tu.HasField('vehicle') else None
        prop = tu.trip_properties if tu.HasField('trip_properties') else None

        cursor.execute('''
            INSERT OR IGNORE INTO trip_update (
                fetched_at, entity_id, timestamp, delay,
                trip_id, route_id, direction_id, start_time, start_date, schedule_relationship,
                mod_modifications_id, mod_affected_trip_id, mod_start_time, mod_start_date,
                vehicle_id, vehicle_label, vehicle_license_plate, vehicle_wheelchair_accessible,
                prop_trip_id, prop_start_date, prop_start_time, prop_shape_id, prop_trip_headsign, prop_trip_short_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fetched_at,
            entity.id,
            tu.timestamp if tu.HasField('timestamp') else None,
            tu.delay if tu.HasField('delay') else None,

            trip.trip_id if trip and trip.HasField('trip_id') else None,
            trip.route_id if trip and trip.HasField('route_id') else None,
            trip.direction_id if trip and trip.HasField('direction_id') else None,
            trip.start_time if trip and trip.HasField('start_time') else None,
            trip.start_date if trip and trip.HasField('start_date') else None,
            trip.schedule_relationship if trip and trip.HasField('schedule_relationship') else None,

            mod.modifications_id if mod and mod.HasField('modifications_id') else None,
            mod.affected_trip_id if mod and mod.HasField('affected_trip_id') else None,
            mod.start_time if mod and mod.HasField('start_time') else None,
            mod.start_date if mod and mod.HasField('start_date') else None,

            veh.id if veh and veh.HasField('id') else None,
            veh.label if veh and veh.HasField('label') else None,
            veh.license_plate if veh and veh.HasField('license_plate') else None,
            veh.wheelchair_accessible if veh and veh.HasField('wheelchair_accessible') else None,

            prop.trip_id if prop and prop.HasField('trip_id') else None,
            prop.start_date if prop and prop.HasField('start_date') else None,
            prop.start_time if prop and prop.HasField('start_time') else None,
            prop.shape_id if prop and prop.HasField('shape_id') else None,
            prop.trip_headsign if prop and prop.HasField('trip_headsign') else None,
            prop.trip_short_name if prop and prop.HasField('trip_short_name') else None
        ))

        for stu in tu.stop_time_update:
            arr = stu.arrival if stu.HasField('arrival') else None
            dep = stu.departure if stu.HasField('departure') else None
            st_prop = stu.stop_time_properties if stu.HasField('stop_time_properties') else None

            cursor.execute('''
                INSERT INTO stop_time_update (
                    fetched_at, trip_entity_id, stop_sequence, stop_id,
                    arrival_delay, arrival_time, arrival_uncertainty, arrival_scheduled_time,
                    departure_delay, departure_time, departure_uncertainty, departure_scheduled_time,
                    departure_occupancy_status, schedule_relationship,
                    prop_assigned_stop_id, prop_stop_headsign, prop_pickup_type, prop_drop_off_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                fetched_at,
                entity.id,
                stu.stop_sequence if stu.HasField('stop_sequence') else None,
                stu.stop_id if stu.HasField('stop_id') else None,

                arr.delay if arr and arr.HasField('delay') else None,
                arr.time if arr and arr.HasField('time') else None,
                arr.uncertainty if arr and arr.HasField('uncertainty') else None,
                arr.scheduled_time if arr and arr.HasField('scheduled_time') else None,

                dep.delay if dep and dep.HasField('delay') else None,
                dep.time if dep and dep.HasField('time') else None,
                dep.uncertainty if dep and dep.HasField('uncertainty') else None,
                dep.scheduled_time if dep and dep.HasField('scheduled_time') else None,

                stu.departure_occupancy_status if stu.HasField('departure_occupancy_status') else None,
                stu.schedule_relationship if stu.HasField('schedule_relationship') else None,

                st_prop.assigned_stop_id if st_prop and st_prop.HasField('assigned_stop_id') else None,
                st_prop.stop_headsign if st_prop and st_prop.HasField('stop_headsign') else None,
                st_prop.pickup_type if st_prop and st_prop.HasField('pickup_type') else None,
                st_prop.drop_off_type if st_prop and st_prop.HasField('drop_off_type') else None
            ))

    conn.commit()
    conn.close()

pb_files = sorted(TRIP_UPDATES_FOLDER.glob("*.pb"))

print(f"Found {len(pb_files)} files to process.")

for pb_filepath in pb_files:
    print(f"Processing: {pb_filepath.name}")
    process_full_trip_updates(pb_filepath, db_filepath)

print("Done.")